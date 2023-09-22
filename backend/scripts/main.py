import time
import status
import monitoring
import signals
import db
import Interfaces
import register
from flask import Flask, request, jsonify
from flask_cors import CORS

# import register


# TODO: improve error handling


# TODO: finish Register

def init():
    monitoring.log(status.INFO, 'Starting LMR-Backend...', True)

    try:
        signals.start_signal_handler()
        db.init()
    except db.NetworkError:
        pass
    except signals.SignalError:
        pass
    except (Exception,):
        pass

    monitoring.log(status.OK, 'Started LMR-Backend', True)


def cleanup(exitcode=0):
    monitoring.log(status.INFO, 'Starting cleanup...', True)

    db.drop_connection()

    monitoring.log(status.OK, 'Finished cleanup', True)

    monitoring.log((status.OK if exitcode == 0 else status.FAIL), 'Exiting with code ' + str(exitcode), True)
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
    print("barcode", barcode)
    return db.GetItemFrontend(barcode)

@app.route('/make_sale', methods=['POST'])
def MakeSale():
    content = request.json
    Items = []
    #Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetItemByID(item["id"])
        newItem.SetCount(item['cnt'])
        Items.append()

    #Save the Transaction
    TransactionID = db.SaveTransaction(Items)

    #Print the Bon
    Register.print(Items,str(TransactionID))

    #Open the Register
    Register.open()
    
    #Should we Update The Remaining Product Count now? Or do that seperatly using the Saved Transaction Data
    
    #What if any should we return !?
    return jsonify(content)
