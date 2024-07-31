import psycopg2
import logging
import time

# -- This File Shall aid in the Upgrade from the first DB Layout to the Second one
# -- First Make a Backup of the Current Status
# -- Rename All Table by prepending a "o_"
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
Steuer = [ (0.19, "Mehrwertsteuer" ), (0.07, "Reduzierte Mehrwertsteuer")]

# TODO: Existing Product Supplier
ExistingProductSupp = ("Existing Products", "-", "Already Existing Stock")

con = psycopg2.connect(
    f"dbname='{database}' user='{user}' host='{host}' password='{password}'")
cur = con.cursor()

# 1. Transfer the Items

# 1.1 Convert Colors to tags
cur.execute(f"select distinct o_items.color from o_items")
Colors = cur.fetchall()
for color in Colors:
    if color[0] in NoData:
        print(f"Detected No Data Entry for Color: {color}")
        continue
    # Split them using the Delimiter to get all possible Single Values
    for singeColor in color[0].split(Delimiter_Color):
        #print(singeColor)
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
cur.execute(f"select distinct o_items.manufacturer from o_items")
Manufacturers = cur.fetchall()
for manufacturer in Manufacturers:
    #print(manufacturer)
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
for percent, name in Steuer:
    cur.execute(f"select amount from tax where amount = '{percent}'")
    result = len(cur.fetchall())
    if result == 0:
        # Init for that Tax is missing
        cur.execute("insert into tax (name,amount) values ('{}',{})".format(name,percent))
        con.commit()
print("Prepare Tax Done")

# 1.5.2 Prepare Existing Products Supplier
cur.execute(f"select name from supplier where name = '{ExistingProductSupp[0]}'")
result = len(cur.fetchall())
if result == 0:
    # We still need to create The Existing Product Supplier
    cur.execute("insert into supplier (name,url,notes) values ('{}','{}','{}')".format(ExistingProductSupp[0],ExistingProductSupp[1],ExistingProductSupp[2]))
    con.commit()
print("Prepare Supplier Done")

# 1.5.3 Transfer Barcodes
cur.execute(f"select barcode from o_barcodes")
barcodes = cur.fetchall()
for barcode in barcodes:
    if barcode[0] in NoData:
        print(f"Detected No Data Entry for Barcode: {barcode[0]}")
        continue
    cur.execute(f"select barcode from o_barcodes where barcode = '{barcode[0]}'")
    result = len(cur.fetchall())
    if result == 0:
        # New Barcode
        cur.execute("insert into barcode (code) values ('{}')".format(barcode[0]))


def saveTagLink(tag,itemID):
    cur.execute(f"select id from featuretag where tag = '{tag}'")
    tagID = cur.fetchone()[0]
    cur.execute(f"insert into specificitemtag (tag, item) values ({tagID}, {itemID})")
    con.commit()

# 1.5.4 Actually Transfer the Products
cur.execute(f"select * from o_items")
oldItems = cur.fetchall()
for id, name, count, price, manufacturer, color, minCount, details, size, tax in oldItems:
    print(f"id: {id}, name: {name} - {count} - {price} - {manufacturer} - {color} - {minCount} - {details} - {size} - {tax}")
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
        # Get the ID of that Barcode
        cur.execute(f"select id from barcodes where code = '{barcode[0]}'")
        barcodeID = cur.fetchone()[0]
        # Now we can Link to that Barcode
        cur.execute(f"insert into productbarcodes (product, code) values ({specificItemID}, {barcodeID})")
        con.commit()

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

    #