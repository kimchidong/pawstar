import os
import sys
import hashlib
import logging
import importlib.util
from logging.handlers import TimedRotatingFileHandler
import datetime

def hash_ip(ip_address):
    """
    클라이언트 IP를 복호화 불가능한 SHA-256 해시 암호문자로 변환합니다.
    """
    if not ip_address:
        ip_address = "127.0.0.1"
    ip_str = str(ip_address).strip()
    if ',' in ip_str:
        ip_str = ip_str.split(',')[0].strip()
    return hashlib.sha256(ip_str.encode('utf-8')).hexdigest()

class CustomLogFormatter(logging.Formatter):
    """
    요구 로그 포맷:
    [YYYY-MM-DD hh:mm:ss] [LEVEL] [PC 또는 MOBILE] [클라이언트 아이피 해시된 복호화 불가능한 암호문자] - 로그 메세지
    """
    def format(self, record):
        dt_str = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        device = getattr(record, 'device', 'PC')
        ip_hash = getattr(record, 'ip_hash', hash_ip('127.0.0.1'))
        msg = record.getMessage()
        return f"[{dt_str}] [{level}] [{device}] [{ip_hash}] - {msg}"

def setup_logger(logger_name, log_dir, log_filename):
    """
    하루 단위 로테이팅 (when='D', interval=1), 총 7일 (1주일) 보관 (backupCount=7) 로거 생성
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = "log/web" if "web" in log_filename else "log/batch"
        os.makedirs(log_dir, exist_ok=True)
        
    log_file_path = os.path.join(log_dir, log_filename)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when='D',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setFormatter(CustomLogFormatter())
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomLogFormatter())
        logger.addHandler(console_handler)
        
    return logger

def _load_config_module(mod_name):
    """ config.web 또는 config.batch 모듈을 안정적으로 동적 로드 """
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(curr_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    try:
        return importlib.import_module(mod_name)
    except Exception:
        config_path = os.path.join(project_root, f"{mod_name}.py")
        if os.path.exists(config_path):
            spec = importlib.util.spec_from_file_location(mod_name, config_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None

def get_web_logger():
    """ 
    웹 전용 로거 (pawstar-web.log)
    디렉터리 감지 우선순위:
    1. /svc/log/pawstar/web (운영 경로 존재 시 최우선 사용)
    2. config.web.py의 LOG_DIR
    3. log/web (기본 상대경로)
    """
    prd_path = "/svc/log/pawstar/web"
    if os.path.exists(prd_path) or os.getenv("APP_ENV") == "prd":
        log_dir = prd_path
    else:
        config_web = _load_config_module("config.web")
        if config_web and hasattr(config_web, "LOG_DIR"):
            log_dir = config_web.LOG_DIR
        else:
            log_dir = "log/web"
            
    return setup_logger('pawstar_web_logger', log_dir, 'pawstar-web.log')

def get_batch_logger():
    """ 
    배치 전용 로거 (pawstar-batch.log)
    디렉터리 감지 우선순위:
    1. /svc/log/pawstar/batch (운영 경로 존재 시 최우선 사용)
    2. config.batch.py의 LOG_DIR
    3. log/batch (기본 상대경로)
    """
    prd_path = "/svc/log/pawstar/batch"
    if os.path.exists(prd_path) or os.getenv("APP_ENV") == "prd":
        log_dir = prd_path
    else:
        config_batch = _load_config_module("config.batch")
        if config_batch and hasattr(config_batch, "LOG_DIR"):
            log_dir = config_batch.LOG_DIR
        else:
            log_dir = "log/batch"
            
    return setup_logger('pawstar_batch_logger', log_dir, 'pawstar-batch.log')
