import logging

logging.basicConfig(level=logging.INFO)


# Login events
auth_logger = logging.getLogger('auth_logger')
auth_file_handler = logging.FileHandler('logs/auth.log')
auth_formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
auth_file_handler.setFormatter(auth_formatter)
auth_logger.addHandler(auth_file_handler)
auth_logger.propagate = False


# Database events
db_logger = logging.getLogger('db_logger')
db_file_handler = logging.FileHandler('logs/db.log')
db_formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
db_file_handler.setFormatter(db_formatter)
db_logger.addHandler(db_file_handler)
db_logger.propagate = False