"""Django settings for ExamOnline project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "你的Django密钥"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "src.apps.User",
    "src.apps.Question",
    "src.apps.Paper",
    "src.apps.Exam",
    "src.apps.Score",
]

MIDDLEWARE = []

ROOT_URLCONF = "api.urls"
WSGI_APPLICATION = "api.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "你的数据库名称",
        "USER": "root",
        "PASSWORD": "你的数据库密码",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "TIME_ZONE": "Asia/Shanghai",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EXAM_RESULT_ROOT = "ExamResultFiles/"
