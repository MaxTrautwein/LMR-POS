import decimal

from main import app, getRegister
from flask import request, jsonify, abort
from datetime import datetime
import logging
import db
import time
from helpers import jsonify_response, jsonToListOfModel
from models import CartItem, RegisterItem

logger = logging.getLogger('LMR_Log')


# Handles PoS Tasks


# TODO Handle Invalid Data
@app.get('/item')
@jsonify_response
def GetItem() -> CartItem.CartItem:
    barcode = request.args.get('code')
    logger.debug(barcode)
    return db.GetItemFrontend(barcode)


@app.route('/make_sale', methods=['POST'])
def MakeSale():

    content = jsonToListOfModel(request.json, CartItem.CartItem)
    debug = request.args.get('debug', default=False)

    SeparateBons: dict[decimal.Decimal, list[RegisterItem.Item]] = {}

    if len(content) == 0:
        logger.error("Attempted Sale with no Items")
        abort(400)
    # Convert Basket from Frontend into compatible format for Printing
    for item in content:
        newItem = db.GetRegisterItemByID(item.getId())
        newItem.SetCount(item.getCnt())

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

    # What if any should we return !?
    return jsonify("Done")
