"""
MacVoice 데이터베이스 - 단축 명령어 및 사용 기록 저장
"""

import sqlite3
import os
from typing import Optional, List, Dict
from datetime import datetime

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "jarvis.db")


class JarvisDB:
    """JARVIS 데이터베이스 관리"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """테이블 생성"""
        cursor = self.conn.cursor()

        # 단축 명령어 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shortcuts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                command TEXT NOT NULL,
                app_name TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 명령어 사용 기록 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                command TEXT,
                response TEXT,
                success INTEGER DEFAULT 1,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 자주 쓰는 명령어 통계 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT UNIQUE NOT NULL,
                use_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    # === 단축 명령어 관리 ===

    def add_shortcut(self, number: int, name: str, command: str,
                     app_name: str = None, description: str = None) -> bool:
        """단축 명령어 추가/업데이트"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO shortcuts (number, name, command, app_name, description)
                VALUES (?, ?, ?, ?, ?)
            """, (number, name, command, app_name, description))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"단축 명령어 추가 오류: {e}")
            return False

    def get_shortcut(self, number: int) -> Optional[Dict]:
        """번호로 단축 명령어 조회"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM shortcuts WHERE number = ?", (number,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_shortcuts(self) -> List[Dict]:
        """모든 단축 명령어 조회"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM shortcuts ORDER BY number")
        return [dict(row) for row in cursor.fetchall()]

    def delete_shortcut(self, number: int) -> bool:
        """단축 명령어 삭제"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM shortcuts WHERE number = ?", (number,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"단축 명령어 삭제 오류: {e}")
            return False

    # === 명령어 기록 관리 ===

    def log_command(self, user_input: str, command: str = None,
                    response: str = None, success: bool = True):
        """명령어 사용 기록 저장"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO command_history (user_input, command, response, success)
                VALUES (?, ?, ?, ?)
            """, (user_input, command, response, 1 if success else 0))

            # 통계 업데이트
            if command:
                cursor.execute("""
                    INSERT INTO command_stats (command, use_count, last_used)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(command) DO UPDATE SET
                        use_count = use_count + 1,
                        last_used = CURRENT_TIMESTAMP
                """, (command,))

            self.conn.commit()
        except Exception as e:
            print(f"명령어 기록 오류: {e}")

    def get_frequent_commands(self, limit: int = 10) -> List[Dict]:
        """자주 쓰는 명령어 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT command, use_count, last_used
            FROM command_stats
            ORDER BY use_count DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_recent_commands(self, limit: int = 20) -> List[Dict]:
        """최근 명령어 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_input, command, response, success, executed_at
            FROM command_history
            ORDER BY executed_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_learning_summary(self) -> str:
        """AI 학습용 사용 패턴 요약"""
        frequent = self.get_frequent_commands(5)
        recent = self.get_recent_commands(10)

        summary = "사용자 명령어 패턴:\n"

        if frequent:
            summary += "\n자주 쓰는 명령어:\n"
            for cmd in frequent:
                summary += f"- {cmd['command']}: {cmd['use_count']}회 사용\n"

        if recent:
            summary += "\n최근 명령어:\n"
            for cmd in recent[:5]:
                summary += f"- \"{cmd['user_input']}\" → {cmd['command']}\n"

        return summary

    def close(self):
        """연결 종료"""
        self.conn.close()


# 싱글톤 인스턴스
_db_instance = None


def get_db() -> JarvisDB:
    """데이터베이스 인스턴스 가져오기"""
    global _db_instance
    if _db_instance is None:
        _db_instance = JarvisDB()
    return _db_instance


if __name__ == "__main__":
    # 테스트
    db = get_db()

    # 단축 명령어 추가 테스트
    db.add_shortcut(1, "사파리", "OPEN_APP:Safari", "Safari", "사파리 열기")
    db.add_shortcut(2, "크롬", "OPEN_APP:Google Chrome", "Google Chrome", "크롬 열기")
    db.add_shortcut(3, "터미널", "OPEN_APP:Terminal", "Terminal", "터미널 열기")

    # 조회 테스트
    print("단축 명령어 목록:")
    for shortcut in db.get_all_shortcuts():
        print(f"  {shortcut['number']}번: {shortcut['name']} → {shortcut['command']}")

    # 명령어 기록 테스트
    db.log_command("볼륨 올려", "VOLUME_UP", "볼륨 올렸습니다", True)
    db.log_command("사파리 열어", "OPEN_APP:Safari", "사파리 열었습니다", True)

    print("\n자주 쓰는 명령어:")
    for cmd in db.get_frequent_commands():
        print(f"  {cmd['command']}: {cmd['use_count']}회")

    print("\n학습 요약:")
    print(db.get_learning_summary())
