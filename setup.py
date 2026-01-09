"""
ZZABIS 설치 스크립트
"""

from setuptools import setup, find_packages

setup(
    name="zzabis",
    version="1.0.0",
    description="AI 음성 타이핑 도우미 - 음성을 텍스트로 변환하고 스타일 변환",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/your-repo/zzabis",
    packages=find_packages(),
    py_modules=[
        "main",
        "ui",
        "ai_agent",
        "speech_openai",
        "commands",
        "config",
        "settings_dialog",
    ],
    install_requires=[
        "PyQt6>=6.4.0",
        "pynput>=1.7.6",
        "pyaudio>=0.2.13",
        "numpy>=1.24.0",
        "openai>=1.0.0",
        "sounddevice>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "zzabis=main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Processing",
    ],
)
