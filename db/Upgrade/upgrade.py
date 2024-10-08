import psycopg2
import logging
import time

# -- This File Shall aid in the Upgrade from the first DB Layout to the Second one
# -- First Make a Backup of the Current Status
# -- Rename All Table by prepending a "o_"
# This can be done via:
#   sed -i 's/barcodes/o_barcodes/g' dump.sql
#   sed -i 's/items/o_items/g' dump.sql
#   sed -i 's/position/o_position/g' dump.sql
#   sed -i 's/transaction/o_transaction/g' dump.sql
#   sed -i 's/o_transaction_o_position/o_transaction_position/g' dump.sql
# -- Load the new InitDB and create the new Tables


# TODO: Fill out your Login Data
password = "test"
user = "postgres"
database = "inventory"
host = "localhost"

# TODO: Maybe Append Options
NoData = ['', '-']
Delimiter_Color = '/'
Delimiter_Details = ';'

# TODO: Init Steuer
Steuer = [(0.19, "Mehrwertsteuer"), (0.07, "Reduzierte Mehrwertsteuer")]

# TODO: Existing Product Supplier
ExistingProductSupp = ("Existing Products", "-", "Already Existing Stock")
ExistingProductSuppID = -1

con = psycopg2.connect(
    f"dbname='{database}' user='{user}' host='{host}' password='{password}'")
cur = con.cursor()


# 1. Transfer the Items
# 1.1 Convert Colors to tags
def ConvertColorsToTags():
    global color, result
    cur.execute(f"select distinct o_items.color from o_items")
    Colors = cur.fetchall()
    for color in Colors:
        if color[0] in NoData:
            print(f"Detected No Data Entry for Color: {color}")
            continue
        # Split them using the Delimiter to get all possible Single Values
        for singeColor in color[0].split(Delimiter_Color):
            # print(singeColor)
            # Save them if they don't already Exist

            # Check if that color already exists
            cur.execute(f"select tag from featuretag where tag = '{singeColor}'")
            result = len(cur.fetchall())
            if result == 0:
                # This is a new Color
                cur.execute("insert into featuretag (tag) values ('{}')".format(singeColor))
                con.commit()
    print("Convert Colors to tags Complete")


# 1.2 Convert Manufacture
def ConvertManufactures():
    global manufacturer, result
    cur.execute(f"select distinct o_items.manufacturer from o_items")
    Manufacturers = cur.fetchall()
    for manufacturer in Manufacturers:
        # print(manufacturer)
        if manufacturer[0] in NoData:
            print(f"Detected No Data Entry for Manufacturer: {manufacturer}")
            continue

        # Check if we have already created this Manufacturer
        cur.execute(f"select name from manufacturer where name = '{manufacturer[0]}'")
        result = len(cur.fetchall())
        if result == 0:
            # This is a new Manufacturer
            cur.execute("insert into manufacturer (name) values ('{}')".format(manufacturer[0]))
            con.commit()
    # 1.2.1 Check for the Unknown Option
    cur.execute(f"select name from manufacturer where name = 'Unknown'")
    result = len(cur.fetchall())
    if result == 0:
        cur.execute("insert into manufacturer (name) values ('Unknown')")
        con.commit()
    print("Convert Manufacturers to tags Complete")


# 1.3 Convert Size to Tags
def ConvertSizeToTags():
    global size, sizeStrip, result
    cur.execute(f"select distinct o_items.size from o_items")
    Sizes = cur.fetchall()
    for size in Sizes:
        # We should Strip the Size
        sizeStrip = size[0].strip()
        if sizeStrip in NoData:
            print(f"Detected No Data Entry for Size: {sizeStrip}")
            continue
        # print(sizeStrip)
        cur.execute(f"select tag from featuretag where tag = '{sizeStrip}'")
        result = len(cur.fetchall())
        if result == 0:
            # New Size
            cur.execute("insert into featuretag (tag) values ('{}')".format(sizeStrip))
            con.commit()
    print("Convert Sizes to tags Complete")


# 1.4 Convert Details to Tags
def ConvertDetailsToTags():
    global detail, detailStrip, result
    cur.execute(f"select distinct o_items.details from o_items")
    Details = cur.fetchall()
    for detail in Details:
        for detailPart in detail[0].split(Delimiter_Details):
            detailStrip = detailPart.strip()
            # print(detailStrip)
            if detailStrip in NoData:
                print(f"Detected No Data Entry for Detail: {detailStrip}")
                continue
            cur.execute(f"select tag from featuretag where tag = '{detailStrip}'")
            result = len(cur.fetchall())
            if result == 0:
                # New Detail
                cur.execute("insert into featuretag (tag) values ('{}')".format(detailStrip))
                con.commit()
    print("Convert Details to tags Complete")


# 1.5 Prepare an Existing Products "Purchase"
# 1.5.1 Prepare Tax
def PrepareTax():
    global name, result
    for percent, name in Steuer:
        cur.execute(f"select amount from tax where amount = '{percent}'")
        result = len(cur.fetchall())
        if result == 0:
            # Init for that Tax is missing
            cur.execute("insert into tax (name,amount) values ('{}',{})".format(name, percent))
            con.commit()
    print("Prepare Tax Done")


# 1.5.2 Prepare Existing Products Supplier
def PrepareExistingProductSupp():
    global result, ExistingProductSuppID
    cur.execute(f"select name from supplier where name = '{ExistingProductSupp[0]}'")
    result = len(cur.fetchall())
    if result == 0:
        # We still need to create The Existing Product Supplier
        cur.execute(
            "insert into supplier (name,url,notes) values ('{}','{}','{}') returning id".format(ExistingProductSupp[0],
                                                                                                ExistingProductSupp[1],
                                                                                                ExistingProductSupp[2]))
        ExistingProductSuppID = cur.fetchone()[0]
        con.commit()
    print("Prepare Supplier Done")




def saveTagLink(tag, itemID):
    cur.execute(f"select id from featuretag where tag = '{tag}'")
    tagID = cur.fetchone()[0]
    cur.execute(f"insert into specificitemtag (tag, item) values ({tagID}, {itemID})")
    con.commit()


OldToNewItemID = {}
OldToNewPositionID = {}
OldToNewTransactionID = {}


# 1.5.4 Actually Transfer the Products
def TransferItems():
    global id, name, count, price, manufacturer, color, size, tax, barcode, detail, detailStrip, sizeStrip
    cur.execute(f"select * from o_items")
    oldItems = cur.fetchall()
    for id, name, count, price, manufacturer, color, minCount, details, size, tax, bon_name in oldItems:
        print(
            f"id: {id}, name: {name} - {count} - {price} - {manufacturer} - {color} - {minCount} - {details} - {size} - {tax} - {bon_name}")
        if manufacturer in NoData:
            manufacturer = "Unknown"
        cur.execute(f"select id from manufacturer where name = '{manufacturer}'")
        manufacturerID = cur.fetchone()[0]
        cur.execute(f"insert into specificitem (name, manufacturer) values ('{name}','{manufacturerID}') returning id")
        specificItemID = cur.fetchone()[0]
        con.commit()

        cur.execute(f"select barcode from o_barcodes where item = {id}")
        linkedBarcodes = cur.fetchall()
        for barcode in linkedBarcodes:
            if barcode[0] in NoData:
                print(f"Detected No Data Entry for Barcode: {barcode[0]}")
                continue
            # Now we can Save the Barcode
            cur.execute(f"insert into barcode (code, product) values ('{barcode[0]}', {specificItemID})")
            con.commit()

            cur.execute(f"select barcode from barcode where code = '{barcode[0]}'")
            duplicateCheck = len(cur.fetchall())
            if duplicateCheck > 1:
                # Error we have a duplicate
                print(f"Duplicate Barcode: {barcode[0]} - ACTION NEEDED")


        # Lets Link the Tags
        for singleColor in color.split(Delimiter_Color):
            if singleColor in NoData:
                print(f"Detected No Data Entry for Color: {singleColor}")
                continue
            # Get the ID of that Color
            saveTagLink(singleColor, specificItemID)
        for detail in details.split(Delimiter_Details):
            detailStrip = detail.strip()
            if detailStrip in NoData:
                print(f"Detected No Data Entry for Detail: {detailStrip}")
                continue
            # Get the ID of that Detail
            saveTagLink(detailStrip, specificItemID)
        sizeStrip = size.strip()
        if sizeStrip in NoData:
            print(f"Detected No Data Entry for Size: {sizeStrip}")
        else:
            saveTagLink(sizeStrip, specificItemID)

        # Transfer Item Group
        cur.execute(
            f"insert into itemgroup (name, bon_name, min_cnt)  Values ('{name}', '{bon_name}', {minCount}) returning id")
        groupID = cur.fetchone()[0]
        con.commit()

        # Save the ID Relation so that we can reconstruct the Transactions
        OldToNewItemID[id] = specificItemID

        # Find the Matching Tax ID
        cur.execute(f"select id from tax where amount = {tax}")
        TaxID = cur.fetchone()[0]

        # Register a Purchase for the Existing Stock
        cur.execute(
            f"insert into purchase (specificitem, cnt, supplier, buyprice, tax, notes) Values ({specificItemID},"
            f" {count}, {ExistingProductSuppID}, {0.00}, {TaxID},'Existing Items - DB Upgrade')")
        con.commit()

        # Configure the Price for that Item
        cur.execute(f"insert into itempricehistory (item, price, tax) Values ({groupID},{price},{TaxID}) ")
        con.commit()

        # Link the Product in specifictogroup
        cur.execute(f"insert into specifictogroup (itemgroup, specific) Values ({groupID},{specificItemID}) ")
        con.commit()



# 1.6 Reconstruct the Purchases
def ReconstructPurchases():
    global id, count
    # 1.6.1 Positions
    cur.execute("select * from o_position")
    positions = cur.fetchall()
    for id, product, count, total in positions:
        cur.execute(f"insert into position (product, count) Values ({product}, {count}) returning id")
        OldToNewPositionID[id] = cur.fetchone()[0]
        con.commit()
    # 1.6.2 Transactions
    cur.execute("select * from o_transaction")
    transactions = cur.fetchall()
    for id, personal, saleDate in transactions:
        cur.execute("insert into transaction (personal, sale_date) Values (%s, %s) returning id"
                    , (personal, saleDate))
        OldToNewTransactionID[id] = cur.fetchone()[0]
        con.commit()
    # 1.6.3 Transaction Positions
    cur.execute(f"select * from o_transaction_position")
    transactionPositions = cur.fetchall()
    for id, oPos, oTrans in transactionPositions:
        cur.execute(f"insert into transaction_position (pos, trans) "
                    f"Values ({OldToNewPositionID[oPos]}, {OldToNewTransactionID[oTrans]})")
        con.commit()
    print("Done with Transfer")


def ConvertToNewVersion():
    ConvertColorsToTags()
    ConvertManufactures()
    ConvertSizeToTags()
    ConvertDetailsToTags()
    PrepareTax()
    PrepareExistingProductSupp()
    TransferItems()
    ReconstructPurchases()


ConvertToNewVersion()

# 1.7 Cleanup
# We had to create ItemGroups for each Specific Item in ordered to preserve Transactions
# We might have Specific Items that where never sold, so those linked ItemGroups may be removed alog
# With the relevant history and linking
cur.execute(f"select id from specificitem where id not in (select distinct position.product from position)")
unSoldProducts = [item[0] for item in cur.fetchall()]
for id in unSoldProducts:
    # Now we need the Relevant Group that specificitem is in
    cur.execute(f"select itemgroup from specifictogroup where specific = {id}")
    groupID = cur.fetchone()[0]

    # itempricehistory holds the previous Price of an Unsold Item
    # We might want to preserve that price for future reference
    cur.execute(f"select * from GetCurrentSpecificItemPriceAndTax({id})")
    price, tax = cur.fetchone()
    oldPriceStr = f"Old Price: {price} Tax: {tax}"
    cur.execute(f"UPDATE specificitem SET notes = '{oldPriceStr}' WHERE id = {id}")
    con.commit()

    cur.execute(f"delete from itempricehistory where item = {groupID}")
    con.commit()
    cur.execute(f"delete from specifictogroup where itemgroup = {groupID}")
    con.commit()

    cur.execute(f"select bon_name, min_cnt from itemgroup where id = {groupID}")
    bonName, minCount = cur.fetchone()

    # Since the item group also saves the min count and bon_name, and we don't want
    # to lose data save them to the override before removing the group
    cur.execute(f"UPDATE specificitem SET min_cnt = {minCount}  WHERE id = {id}")
    con.commit()
    # No need to save an Empty bonName
    if bonName not in NoData:
        cur.execute(f"UPDATE specificitem SET bon_name = '{bonName}'  WHERE id = {id}")
        con.commit()

    cur.execute(f"delete from itemgroup where id = {groupID}")
    con.commit()
print("Removed Unused Pseudo Products")

print("Please Feel free to Deprecate the Current Pseudo Items as they are directly linked to products")



