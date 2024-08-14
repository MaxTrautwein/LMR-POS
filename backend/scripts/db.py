import decimal
from datetime import datetime

import psycopg2
import logging
import time
from models import CartItem, RegisterItem, ExportData
from models.ExportItem import ExportItem

logger = logging.getLogger('LMR_Log')


# Get SpecificItem ID by Barcode
def GetItemID(barcode: str) -> int:
    execute(f"select * from GetSpecificItemID('{barcode}')")
    return cur.fetchone()[0]


# TODO Update for V5
# Get all Tags linked to that pseudo Item
def GetItemTags(itemID: int) -> list[str]:
    tags: list[str] = []
    execute(f"select * from GetLinkedTags({itemID})")
    tagRes = cur.fetchall()
    for tag in tagRes:
        tags.append(tag[0])
    return tags


# Returns the Price and Tax of a Pseudo Item
def GetItemPriceAndTax(itemID: int) -> tuple[decimal.Decimal, decimal.Decimal]:
    execute(f"select * from GetCurrentSpecificItemPriceAndTax({itemID})")
    return cur.fetchall()[0]


# Get the Name and bon Name of a Pseudo Item
def GetItemName(itemID: int) -> str:
    execute(f"select name from itemgroup where id = (select id from GetCurrentSpecificItemGroup({itemID}))")
    return cur.fetchone()[0]


def GetItemBonName(itemID: int) -> str:
    execute(f"select * from GetBonName({itemID})")
    return cur.fetchone()[0]


def GetItemFrontend(barcode: str) -> CartItem.CartItem:
    # Get the Item ID by barcode
    itemId = GetItemID(barcode)

    tags = GetItemTags(itemId)
    price, tax = GetItemPriceAndTax(itemId)
    name = GetItemName(itemId)
    bon_name = GetItemBonName(itemId)
    item = CartItem.CartItem(itemId, name, bon_name, price, tax, tags)

    return item


# Get an Instance of one RegisterItem by its ID
def GetRegisterItemByID(itemId: int) -> RegisterItem.Item:
    price, tax = GetItemPriceAndTax(itemId)
    bon_name = GetItemBonName(itemId)

    if bon_name is None or bon_name == '':
        bon_name = GetItemName(itemId)

    return RegisterItem.Item(itemId, bon_name, price, tax, 1)


# Save a Transaction and Return the Time and ID
def SaveTransaction(Items: list[RegisterItem.Item]) -> tuple[int, datetime]:
    pos = []

    # Get Transaction ID
    # TODO Add user System
    execute(
        "insert into transaction (personal, sale_date) VALUES ('{}',clock_timestamp()) returning id, sale_date;".format(
            "Max Musterman"))
    trans_id, sale_date = cur.fetchone()
    commit()
    for item in Items:
        # Create Position
        count = item.count
        execute("insert into position (product, count) VALUES ({},{}) returning id;"
                .format(item.id, count))
        pos.append(cur.fetchone()[0])
        commit()
    for pos_id in pos:
        # Create Links
        execute("insert into transaction_position (pos, trans) VALUES ({},{});".format(pos_id, trans_id))
        commit()
    execute("update transaction set sale_date=clock_timestamp() where id={};".format(trans_id))
    commit()
    logger.info("Transaction Saved")
    return trans_id, sale_date


def GetItemPriceAndTaxAtPointInTime(itemID: int, pointInTime: datetime) -> tuple[decimal.Decimal, decimal.Decimal]:
    execute("select * from GetSpecificItemPriceAndTax({}, '{}')".format(itemID, pointInTime))
    return cur.fetchall()[0]


def getItemIDsAndCntInTransaction(transactionID: int) -> list[tuple[int, int]]:
    execute("select p.product, p.count from transaction_position tp, position p "
            "where tp.pos = p.id and tp.trans = {}".format(transactionID))
    return cur.fetchall()


def getTotalAndTaxForTransaction(transactionID: int) -> tuple[decimal.Decimal, decimal.Decimal]:
    execute("select transaction.sale_date from transaction where id={};".format(transactionID))
    sale_date = cur.fetchone()[0]
    total = decimal.Decimal(0)
    items = getItemIDsAndCntInTransaction(transactionID)
    tax = decimal.Decimal(0)
    for item in items:
        price, _tax = GetItemPriceAndTaxAtPointInTime(item[0], sale_date)
        total += item[1] * price
        if tax == 0:
            tax = _tax
        elif tax != _tax:
            logger.error("Tax mismatch")
    return total, tax


def GenerateTransactionExportSheet(minimumTransactionIdExclusive) -> list[ExportData.ExportData]:
    logger.info("Generate Export for Sale after " + str(minimumTransactionIdExclusive))

    execute("select * from GetTransactionsAfter({})".format(minimumTransactionIdExclusive))
    data = cur.fetchall()
    ReturnData: list[ExportData.ExportData] = []
    for saleDay, saleMonth, exportDay, exportMonth, transactionId in data:
        total, tax = getTotalAndTaxForTransaction(transactionId)
        execute("select t.sale_date from transaction t where t.id={};".format(transactionId))
        date = cur.fetchone()[0]
        logger.debug(type(data))

        exportItems: list[ExportItem] = []
        items = getItemIDsAndCntInTransaction(transactionId)
        for item in items:
            price, tax = GetItemPriceAndTaxAtPointInTime(item[0], date)
            exportItems.append(ExportItem(GetItemBonName(item[0]),item[1],price,tax))
        logger.warning(type(date.isoformat()))
        ReturnData.append(
            ExportData.ExportData(transactionId, saleDay, saleMonth, exportDay, exportMonth,
                                  f"LMR Verkauf ID:  {transactionId}", total, tax, date.isoformat(), exportItems))
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
