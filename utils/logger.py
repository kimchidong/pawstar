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

def _load_config_module(mod_filename):
    """ config.web.py 또는 config.batch.py 모듈을 spec_from_file_location으로 정확하게 동적 로드 """
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(curr_dir)
    
    candidates = [
        os.path.join(project_root, mod_filename),
        os.path.join(os.getcwd(), mod_filename)
    ]
    
    for path in candidates:
        if os.path.exists(path):
            try:
                module_alias = mod_filename.replace('.', '_')
                spec = importlib.util.spec_from_file_location(module_alias, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
            except Exception as e:
                print(f"Error loading {path}: {e}")
                
    return None

def get_web_logger():
    """ 
    config.web.py에 정의된 LOG_DIR(APP_ENV 환경에 따른 local/prd 구분)을 정직하게 참조하는 웹 전용 로거
    """
    config_web = _load_config_module("config.web.py")
    if config_web and hasattr(config_web, "LOG_DIR"):
        log_dir = config_web.LOG_DIR
    else:
        log_dir = "log/web"
            
    return setup_logger('pawstar_web_logger', log_dir, 'pawstar-web.log')

def get_batch_logger():
    """ 
    config.batch.py에 정의된 LOG_DIR(APP_ENV 환경에 따른 local/prd 구분)을 정직하게 참조하는 배치 전용 로거
    """
    config_batch = _load_config_module("config.batch.py")
    if config_batch and hasattr(config_batch, "LOG_DIR"):
        log_dir = config_batch.LOG_DIR
    else:
        log_dir = "log/batch"
            
    return setup_logger('pawstar_batch_logger', log_dir, 'pawstar-batch.log')
