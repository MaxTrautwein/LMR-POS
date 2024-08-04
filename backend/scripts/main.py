import logging
import signals
import db
import register
from flask import Flask, jsonify
from flask_cors import CORS
from models import PseudoItem, BaseModel
from functools import wraps

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


# Wrapper Function, so that we can Return Classes defiled in models
# Each Model is a Child of BaseModel, allowing us to easily convert them to a Dict
def jsonify_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, BaseModel.BaseModel):
            return jsonify(result.to_dict())
        return result

    return wrapper


# Init Register
Register = register.Register("/dev/ttyS0")


def getRegister() -> register.Register:
    return Register

@app.get("/test")
@jsonify_response
def test():
    # item = PseudoItem.PseudoItem("name", "desc", 12.3)
    # return item
    return db.GetItemPriceAndTax(27)