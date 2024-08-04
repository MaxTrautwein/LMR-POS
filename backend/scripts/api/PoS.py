from main import app, getRegister
from flask import request, jsonify, abort
from datetime import datetime
import logging
import db
import time

logger = logging.getLogger('LMR_Log')


# Handles PoS Tasks


# TODO Handle Invalid Data
@app.get('/item')
def GetItem():
    barcode = request.args.get('code')
    return db.GetItemFrontend(barcode)


@app.route('/make_sale', methods=['POST'])
def MakeSale():
    content = request.json
    debug = request.args.get('debug', default=False)

    SeparateBons = {}

    if len(content) == 0:
        logger.error("Attempted Sale with no Items")
        abort(400)
    # Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetItemByID(item["id"])
        newItem.SetCount(item['cnt'])

        tax = newItem.tax
        if tax not in SeparateBons:
            SeparateBons[tax] = []
        SeparateBons[tax].append(newItem)
    logger.debug(SeparateBons)
    for _, taxBracket in SeparateBons.items():
        # Save the Transaction
        if not debug:
            TransactionID, date = db.SaveTransaction(taxBracket)
        else:
            TransactionID = 0  # Debugging Sale ID (0 will never be a real Sale ID)
            date = datetime.now()  # Get the Current Time
        logger.debug(f"printing on for {taxBracket}")
        # Print the Bon
        getRegister().print(taxBracket, date, f"{TransactionID:011}")
        # TODO Add function to check if the printer is ready
        # TODO Optionally as a wait function on the print command
        time.sleep(5)

    # Open the Register
    getRegister().open()

    # Should we Update The Remaining Product Count now? Or do that separately using the Saved Transaction Data

    # What if any should we return !?
    return jsonify(content)
