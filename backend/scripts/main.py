import logging
import signals
import db
import register
from flask import Flask, request
from flask_cors import CORS
from models import CartItem, BaseModel
from helpers import jsonToListOfModel

logger = logging.getLogger('LMR_Log')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)


# TODO: improve error handling


# TODO: finish Register

def init():
    logger.info('Starting LMR-Backend...')

    try:
        signals.start_signal_handler()
        db.init()
    except db.NetworkError:
        pass
    except signals.SignalError:
        pass
    except (Exception,):
        pass

    logger.info('Started LMR-Backend')


# TODO This appears to be unused
def cleanup(exitcode=0):
    logger.info('Starting cleanup...')

    db.drop_connection()

    logger.info('Finished cleanup')

    if exitcode == 0:
        logger.info('Exiting with code ' + str(exitcode))
    else:
        logger.error('Exiting with code ' + str(exitcode))
    exit(exitcode)


app = Flask(__name__)
CORS(app)

init()



# Init Register
Register = register.Register("/dev/ttyS0")


def getRegister() -> register.Register:
    return Register



import api.PoS
import api.Export
import api.Admin