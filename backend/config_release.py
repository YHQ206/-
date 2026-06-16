"""
发布版本配置文件 - 使用 SQLite 数据库

使用方法：
1. 将此文件重命名为 config.py（备份原 config.py）
2. 或者设置环境变量 DATABASE_URL
"""
import os


class Config:
    # 默认使用 SQLite，无需安装数据库
    # 如果需要使用 MySQL，可以设置环境变量 DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///shuti.db'  # SQLite 数据库文件会创建在 backend 目录下
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'shuti-quiz-secret-key-2024')
