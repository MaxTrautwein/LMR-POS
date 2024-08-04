from main import app
from flask import request, jsonify, render_template
import logging
import db

logger = logging.getLogger('LMR_Log')
# Handles the Export of Purchases


@app.get('/Export/Sheet')
def GetExportSheet():
    id = request.args.get('id')
    return db.GenerateTransactionExportSheet(id)


# There has to be a better way to do that
PageSetup = []


@app.get('/Export/PDF')
def GetPDF_Printout():
    logger.info(PageSetup)
    return render_template("TransactionPDF.html", data=PageSetup)


@app.route('/Export/Generate', methods=['POST'])
def GeneratePDF_Printout():
    # Min Height 1/4 1-2 Items
    # Max Height 1 --> 39 Items
    # If more then Max Print as Error Call for Manual Action
    # In terms of Space
    #  H1 === 3 Items
    #  Accounting == 7 Items
    #  <hr> == 3 Items
    #  Min Height 15 "Units"
    #  1 Page Max 4 * 15 = 60 "Units"
    #
    content = request.json
    logger.debug(content)
    PageSpace = 60
    # Array of
    # {
    # "TransactionID":20
    # "SaleID":1(
    # })

    TransactionData = []
    for Sale in content:
        TransactionData.append(db.GetTransactionData(Sale["SaleID"]))
        # Append Transaction Number
        TransactionData[-1]["TransactionID"] = Sale["TransactionID"]
        TransactionData[-1]["Total"] = Sale["Total"]
    # Build up the Page Composition
    PageSetup.clear()
    PageSetup.append({
        "free": PageSpace,
        "Items": []
    })
    logger.info(PageSetup)
    for transaction in TransactionData:
        # Calculate the required Space
        items = len(transaction["items"])
        if items <= 2:
            size = 15
        else:
            size = 15 + items - 2

        # Check if it still fits
        if size > PageSetup[-1]["free"]:
            # We need a new Page
            PageSetup.append({
                "free": PageSpace,
                "Items": []
            })
        # Now We have space by definition
        # Insert the Transaction into the Page
        # Subtract Required Space
        PageSetup[-1]["free"] -= size
        # Add the Content
        # Sanity Check Not over the Max
        if size > 60:
            logger.error(
                "Transaction ID: " + str(transaction["id"]) + " Is over the Size Limitation.... Size: " + str(size))
            # Maybe Add an Error Info To the Page
            transaction["date"] = "ERROR"
        PageSetup[-1]["Items"].append(transaction)
    return jsonify(content)