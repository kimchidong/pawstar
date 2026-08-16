import os

# Environment: 'local' or 'prd'
APP_ENV = os.getenv("APP_ENV", "local")

# Log Directory based on environment
if APP_ENV == "prd":
    LOG_DIR = "/svc/log/pawstar/web"
    DB_CONFIG = {
        "host": "210.114.22.228",
        "port": 3361,
        "user": "kcd",
        "password": "cdKim3315!",
        "database": "DB_PST",
        "charset": "utf8mb4"
    }
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_PRD", os.getenv("GOOGLE_CLIENT_ID", ""))
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET_PRD", os.getenv("GOOGLE_CLIENT_SECRET", ""))
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI_PRD", os.getenv("GOOGLE_REDIRECT_URI", "https://pawstar.co.kr/auth/google/callback"))
else:
    LOG_DIR = "log/web"
    DB_CONFIG = {
        "host": "localhost",
        "port": 3361,
        "user": "kcd",
        "password": "1q2w3e4r5t!",
        "database": "DB_PST",
        "charset": "utf8mb4"
    }
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8003/auth/google/callback")


def get_google_config():
    """
    현재 APP_ENV 및 환경 변수에 맞는 Google OAuth 설정 정보(client_id, client_secret, redirect_uri)를 반환합니다.
    """
    current_env = os.getenv("APP_ENV", "local")
    if current_env == "prd":
        client_id = os.environ.get('GOOGLE_CLIENT_ID_PRD', os.environ.get('GOOGLE_CLIENT_ID', ''))
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET_PRD', os.environ.get('GOOGLE_CLIENT_SECRET', ''))
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI_PRD', os.environ.get('GOOGLE_REDIRECT_URI', 'https://pawstar.co.kr/auth/google/callback'))
    else:
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8003/auth/google/callback')

    return client_id, client_secret, redirect_uri
