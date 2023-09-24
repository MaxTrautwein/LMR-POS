import logging
import signals
import db
import register
from flask import Flask, request, jsonify
from flask_cors import CORS

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


def cleanup(exitcode=0):
    logger.info('Starting cleanup...')

    db.drop_connection()

    logger.info('Finished cleanup')

    if(exitcode == 0):
        logger.info('Exiting with code ' + str(exitcode))
    else:
        logger.error('Exiting with code ' + str(exitcode))
    exit(exitcode)


def test():
    try:
        db.execute("SELECT name FROM items WHERE cnt <= 5 AND price <= '$1.00'")
        print(db.fetch())
    except db.ExecError:
        return
    except db.FetchError:
        return




app = Flask(__name__)
CORS(app)

init()

#Init Register
Register = register.Register("/dev/ttyS0")

#TODO Handle Invalid Data
@app.get('/item')
def GetItem():
    barcode = request.args.get('code')
    return db.GetItemFrontend(barcode)

@app.route('/make_sale', methods=['POST'])
def MakeSale():
    content = request.json
    Items = []
    #Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetItemByID(item["id"])
        newItem.SetCount(item['cnt'])
        Items.append(newItem)

    #Save the Transaction
    TransactionID = db.SaveTransaction(Items)

    #Print the Bon
    Register.print(Items,f"{TransactionID:012}")

    #Open the Register
    Register.open()
    
    #Should we Update The Remaining Product Count now? Or do that seperatly using the Saved Transaction Data
    
    #What if any should we return !?
    return jsonify(content)

@app.route('/AddNewItem', methods=['POST'])
def AddNewItem():
    content = request.json
    db.AddNewItem(content)
    #What if any should we return !?
    return jsonify(content)