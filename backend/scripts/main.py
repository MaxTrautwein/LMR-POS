import logging
import signals
import db
import register
from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from datetime import datetime
import time


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

    SeperateBons = {}
    
    if (len(content) == 0):
        logger.error("Attemped Sale with no Items")
        abort(400)
    #Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetItemByID(item["id"])
        newItem.SetCount(item['cnt'])

        tax = newItem.tax
        if not tax in SeperateBons:
            SeperateBons[tax] = []
        SeperateBons[tax].append(newItem)
    logger.debug(SeperateBons)
    for _, taxBracked in SeperateBons.items():
        #Save the Transaction
        TransactionID, date = db.SaveTransaction(taxBracked)
        logger.debug(f"printing on for {taxBracked}")
        #Print the Bon
        Register.print(taxBracked,date,f"{TransactionID:011}")
        # TODO Add function to check if the printer is ready
        # TODO Optionally as a wait function on the print command 
        time.sleep(5)


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

@app.get('/ExportSheet')
def GetExportSheet():
    id = request.args.get('id')
    return db.GenerateTransactionExportSheet(id)


#There has to be a better way to do that
PageSetup = []
@app.get('/ExportPDF')
def GetPDF_Printout():
    logger.info(PageSetup)
    return render_template("TransactionPDF.html",data=PageSetup)

@app.route('/GeneratePDF', methods=['POST'])
def GeneratePDF_Printout():
    # Min Hight 1/4 1-2 Items
    # Max Hight 1 --> 39 Items
    # If more then Max Print as Error Call for Manual Action
    # In terms of Space 
    #  H1 === 3 Items
    #  Accounting == 7 Items
    #  <hr> == 3 Items
    #  Min Hight 15 "Units"
    #   1 Page Max 4 * 15 = 60 "Units"
    #
    content = request.json
    logger.debug(content)
    PageSpace = 60
    #Array of
    # {
    # "TransactionID":20
    # "SaleID":1(
    # })

    TranactionData = []
    for Sale in content:
        TranactionData.append( db.GetTransactionData(Sale["SaleID"]))
        #Append Transaction Number
        TranactionData[-1]["TransactionID"] = Sale["TransactionID"]
        TranactionData[-1]["Total"] = Sale["Total"]
    # Build up the Page Composition
    PageSetup.clear()
    PageSetup.append({
                    "free":PageSpace,
                    "Items":[]
                })
    logger.info(PageSetup)
    for transaction in TranactionData:
        # Calculate the requierd Space
        items = len(transaction["items"])
        if (items <= 2):
            size = 15
        else:
            size = 15 + items - 2
            
        #Check if it still fits
        if (size > PageSetup[-1]["free"]):
            #Wee need a new Page
            PageSetup.append({
                "free":PageSpace,
                "Items":[]
            })
        #Now We have space by definition
        #Insert the Transaction into the Page
        #Substract Reqierd Space
        PageSetup[-1]["free"] -= size
        #Add the Content
        # Sanity Check Not over the Max
        if (size > 60):
            logger.error("Transaction ID: " + str(transaction["id"]) + " Is over the Size Limitation.... Size: " + str(size))
            #Maybe Add a Error Info To the Page
            transaction["date"] = "ERROR"
        PageSetup[-1]["Items"].append(transaction)
    return jsonify(content)


@app.route('/debug_sale', methods=['POST'])
def DebugSale():
    content = request.json

    SeperateBons = {}
    
    if (len(content) == 0):
        logger.error("Attemped Sale with no Items")
        abort(400)
    # Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetItemByID(item["id"])
        newItem.SetCount(item['cnt'])

        tax = newItem.tax
        if not tax in SeperateBons:
            SeperateBons[tax] = []
        SeperateBons[tax].append(newItem)
    for _, taxBracked in SeperateBons.items():
        # Don't save The Transaction for debugging
        TransactionID = 0 # Debugging Sale ID (0 will never be a real Sale ID)
        date = datetime.now() # Get the Current Time
        # Print the Bon
        Register.print(taxBracked,date,f"{TransactionID:011}")

    #Open the Register
    Register.open()

    #What if any should we return !?
    return jsonify(content)

@app.route('/OpenDrawer', methods=['POST'])
def OpenDrawer():
    logger.info("Used Open Drawer Command")
    Register.open()
    return {}

@app.get('/AdminAccess')
def Get_AdminAccess():
    return render_template("AdminAccess.html")