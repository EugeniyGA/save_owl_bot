import logging


def create_logger(file_name: str, name: str):
    # Заводим логгирование
    path = f'logs/{file_name}'
    file_log = logging.FileHandler(path, encoding="UTF-8")
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s: %(levelname)s] %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
