import logging, colorlog

def Logger():
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    cformat = "[%(asctime)s] %(log_color)s%(message)s"
    colors = {'DEBUG': 'cyan',
              'INFO': 'green',
              'WARNING': 'yellow',
              'ERROR': 'red',
              'CRITICAL': 'red,bg_white'}
    formatter = colorlog.ColoredFormatter(cformat, log_colors=colors)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    log = logging.FileHandler('JK.log')
    log.setLevel(logging.DEBUG)
    log.setFormatter(formatter)
    logger.addHandler(log)

    return logging.getLogger(__name__)