import logging
import colors
import signal

logger = logging.getLogger('LMR_Log')

class Interrupt(Exception):
    pass


class SignalError(Exception):
    pass


# Signal Handler to prevent docker from killing python
def signal_handler(_, __):
    logger.info(colors.HEADER + 'Received interrupt')
    raise Interrupt


# catch SIGINT and SIGTERM signals
def start_signal_handler():
    logger.info('Starting signal handlers...')
    try:
        signal.signal(signal.SIGTERM, signal_handler)
    except (Exception,):
        logger.error('Failed to start SIGTERM handler')
        raise SignalError
    else:
        logger.info('Started SIGTERM handler')

    try:
        signal.signal(signal.SIGINT, signal_handler)
    except (Exception,):
        logger.error('Failed to start SIGINT handler')
        raise SignalError
    else:
        logger.info('Started SIGINT handler')
