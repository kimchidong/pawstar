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
