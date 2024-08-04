import decimal

import psycopg2
import logging
import time
import Interfaces
from models import PseudoItem

logger = logging.getLogger('LMR_Log')


# Get Pseudo Item ID by Barcode
def GetItemID(barcode: str) -> int:
    execute(f"select s.pseudo from barcode b, productbarcodes p, specifictopseudo s where"
            f" p.code = b.id and s.specific = p.product and s.deprecated IS NULL and b.code = '{barcode}';")
    return cur.fetchone()[0]


# Get all Tags linked to that pseudo Item
def GetItemTags(itemID: int) -> list[str]:
    tags: list[str] = []
    # Get All Specific Items Linked to that Pseudo Item ID
    execute(f"select specific from specifictopseudo s where s.deprecated IS NULL and s.pseudo = {itemID}")
    specifics = cur.fetchall()
    for specific in specifics:
        # Get all Tags for that Item
        execute(f"select * from GetLinkedTags({specific[0]})")
        tagRes = cur.fetchall()
        for tag in tagRes:
            tags.append(tag[0])
    return tags

# Returns the Price and Tax of a Pseudo Item
def GetItemPriceAndTax(itemID: int) -> tuple[decimal.Decimal, decimal.Decimal]:
    execute(f"select p.price, t.amount from tax t, itempricehistory p "
            f"where t.id = p.tax and p.deprecateddate is NULL and p.item = {itemID}")
    return cur.fetchall()[0]

# Get the Name and bon Name of a Pseudo Item
def GetItemNames(itemID: int) -> tuple[str, str]:
    execute(f"select name, bon_name from item where id = {itemID}")
    return cur.fetchall()[0]


def GetItemFrontend(barcode: str) -> PseudoItem.PseudoItem:
    # Get the Item ID by barcode
    itemId = GetItemID(barcode)

    tags = GetItemTags(itemId)
    price, tax = GetItemPriceAndTax(itemId)
    name, bon_name = GetItemNames(itemId)

    item = PseudoItem.PseudoItem(name, bon_name, price, tax, tags)

    return item


#Get a Instance of one Item by it's ID
def GetItemByID(id):
    execute(
        "select name, price, manufacturer, color,  details, size, tax , coalesce(nullif(bon_name,''),name) from Items where id={};".format(
            id))
    name, price, manufacturer, color, details, size, tax, bon_name = cur.fetchone()
    # TODO maybe Append Interfaces.Item with name as the name & bon_name Logic is now handeled as SQL
    return Interfaces.Item(id, bon_name, price, manufacturer, color, details, size, tax, 1)


#Save a Transaction and Return the ID
def SaveTransaction(Items):
    pos = []

    #Get Transaction ID
    #TODO Add user System
    execute(
        "insert into transaction (personal, sale_date) VALUES ('{}',clock_timestamp()) returning id, sale_date;".format(
            "Max Musterman"))
    trans_id, sale_date = cur.fetchone()
    commit()
    for item in Items:
        #Create Position
        count = item.count
        execute("insert into position (product, count, total) VALUES ({},{},{}) returning id;"
                .format(item.id, count, item.price * count))
        pos.append(cur.fetchone()[0])
        commit()
    for pos_id in pos:
        #Create Links
        execute("insert into transaction_position (pos, trans) VALUES ({},{});".format(pos_id, trans_id))
        commit()
    execute("update transaction set sale_date=clock_timestamp() where id={};".format(trans_id))
    commit()
    return trans_id, sale_date


def AddNewItem(Data):
    name = Data["name"]
    cnt = Data["cnt"]
    price = Data["price"]
    manufacturer = Data["manufacturer"]
    color = Data["color"]
    min_cnt = Data["min_cnt"]
    details = Data["details"]
    size = Data["size"]
    bon_name = Data["bon_name"]
    Barcodes = Data["Barcodes"]
    #Create the item
    execute("insert into Items(name, cnt, price, manufacturer, color, min_cnt, details, size, bon_name) " +
            "values ('{}',{},{},'{}','{}',{},'{}','{}','{}') returning id;"
            .format(name, cnt, price, manufacturer, color, min_cnt, details, size, bon_name))
    id = cur.fetchone()[0]
    commit()

    #Link the Barcodes
    for Barcode in Barcodes:
        execute("insert into barcodes (barcode, item) values ('{}',{})"
                .format(Barcode, id))
        commit()
    #Create the Internal Barcode:
    execute("insert into barcodes (barcode, item) values ('{}',{})"
            .format(f"LMR-{(id - 1):04}", id))
    commit()


def GenerateTransactionExportSheet(id):
    logger.info("Generate Export far Salse after " + str(id))
    execute("SELECT extract(day  from transaction.sale_date) as \"Sale Day\"," +
            "extract(month  from transaction.sale_date) as \"Sale Month\"," +
            "extract(day  from clock_timestamp()) as \"Book Day\"," +
            "extract(month  from clock_timestamp()) as \"Book Month\"," +
            "concat('LMR Verkauf ID: ', transaction.id)," +
            "sum(position.total)," +
            "transaction.id, " +
            "items.tax " +
            "from transaction_position , position, transaction, items" +
            " where transaction_position.trans = transaction.id and transaction_position.pos = position.id" +
            " and transaction.id > {}".format(id) +
            " and items.id = position.product"
            " group by transaction.sale_date, transaction.id, items.tax order by transaction.sale_date;")
    data = cur.fetchall()
    ReturnData = []
    for sale in data:
        ReturnData.append({
            "SaleID": sale[6],
            "SaleDay": sale[0],
            "SaleMonth": sale[1],
            "EntryDay": sale[2],
            "EntryMonth": sale[3],
            "Desc": sale[4],
            "Amount": sale[5],
            "Tax": sale[7]
        })
    return ReturnData


def GetTransactionData(id):
    execute(
        "SELECT transaction.sale_date,position.count, coalesce(nullif(items.bon_name,''),items.name) ,position.total, items.tax from position,transaction_position,items, transaction " +
        "where position.id =  transaction_position.pos and transaction.id = transaction_position.trans and items.id = position.product " +
        "and transaction_position.trans = {}".format(id))
    data = cur.fetchall()
    ReturnData = {
        "date": data[0][0],
        "id": id,
        "items": []
    }
    logger.debug("Response form SQL:")
    logger.debug(data)
    for sale in data:
        ReturnData["items"].append({
            "name": sale[2],
            "cnt": sale[1],
            "price_per": sale[3] / sale[1],
            "tax": sale[4]
        })

    return ReturnData


class NetworkError(Exception):
    pass


class ExecError(Exception):
    pass


class FetchError(Exception):
    pass


class CommitError(Exception):
    pass


# Connection to postgres database
CONNECTION_RETRIES = 3
RETRY_TIMEOUT = 1

con = ...
cur = ...


def init():
    global con, cur
    logger.info('Attempting to connect to database...')
    # setup database connection
    for i in range(CONNECTION_RETRIES):
        try:
            con = psycopg2.connect(
                "dbname='inventory' user='lmr' host='postgres' password='lmrSecretDBPassword'")
            cur = con.cursor()
        except (Exception,):
            logger.error('Can\'t establish connection to database')
        else:
            logger.info('Connected to database')
            return

        time.sleep(RETRY_TIMEOUT)
        logger.info('Reattempting to connect to database')

    logger.critical('Connection to database failed')
    raise NetworkError


def execute(cmd: str):
    try:
        cur.execute(cmd)
    except (Exception,):
        logger.error('DB can\'t exec: ' + cmd)
        if cur.closed:
            logger.warning('database appears to be offline')
            init()
            logger.debug('Retry DB exec: ' + cmd)
            execute(cmd)
        else:
            logger.critical('DB exec error')
            raise ExecError
    else:
        logger.debug('DB exec: ' + cmd)


def fetch():
    try:
        response = cur.fetchall()
    except (Exception,):
        logger.error('DB can\'t fetch')
        if cur.closed:
            logger.warning('database appears to be offline')
            init()
            logger.info('Retry DB fetch')
            response = fetch()
        else:
            logger.critical('DB fetch error')
            raise FetchError
    else:
        logger.debug('DB fetch')
    return response


def commit():
    try:
        con.commit()
    except (Exception,):
        logger.error('DB can\'t commit')
        #TODO Fix that
        if cur.closed:
            logger.warning('database appears to be offline')
            init()
            logger.info('Retry DB commit')
            con.commit()
        else:
            logger.critical('DB commit error')
            raise FetchError
    else:
        logger.debug('DB commit')


def drop_connection():
    if con:
        logger.info('Closing database connection...')
        con.close()
        if con.closed:
            logger.info('Closed database connection')
        else:
            logger.error('Can\'t close database connection')
            logger.warning('Leaving database connection open')
    else:
        logger.warning('Skipping: Close database connection')
