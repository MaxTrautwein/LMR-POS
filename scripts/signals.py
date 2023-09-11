import monitoring
import status
import colors
import signal


class Interrupt(Exception):
    pass


class SignalError(Exception):
    pass


# Signal Handler to prevent docker from killing python
def signal_handler(_, __):
    monitoring.log(status.INFO, colors.HEADER + 'Received interrupt')
    raise Interrupt


# catch SIGINT and SIGTERM signals
def start_signal_handler():
    monitoring.log(status.INFO, 'Starting signal handlers...')
    try:
        signal.signal(signal.SIGTERM, signal_handler)
    except (Exception,):
        monitoring.log(status.OK, 'Failed to start SIGTERM handler')
        raise SignalError
    else:
        monitoring.log(status.OK, 'Started SIGTERM handler')

    try:
        signal.signal(signal.SIGINT, signal_handler)
    except (Exception,):
        monitoring.log(status.OK, 'Failed to start SIGINT handler')
        raise SignalError
    else:
        monitoring.log(status.OK, 'Started SIGINT handler')
