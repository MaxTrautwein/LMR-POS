import psycopg2
import logging
import time
import Interfaces

logger = logging.getLogger('LMR_Log')


def GetItemID(barcode):
    execute("select item from barcodes where barcode='{}';".format(barcode))
    return cur.fetchone()[0]

def GetItemFrontend(barcode):
    # Get the Item ID by barcode
    id = GetItemID(barcode)
    # Get the Item Data
    execute("select name, price, manufacturer, color,  details, size, tax from Items where id={};".format(id))
    name, price, manufacturer, color,  details, size, tax = cur.fetchone()
    #return Item(id, name, price, manufacturer, color,  details, size, tax)
    return {"id":id,
            "name":name,
            "manufacturer":manufacturer,
            "color":color,
            "size":size,
            "details":details,
            "price":price,
            "tax":tax} 


#Get a Instance of one Item by it's ID
def GetItemByID(id):
    execute("select name, price, manufacturer, color,  details, size, tax , coalesce(nullif(bon_name,''),name) from Items where id={};".format(id))
    name, price, manufacturer, color,  details, size, tax, bon_name = cur.fetchone()
    # TODO maybe Append Interfaces.Item with name as the name & bon_name Logic is now handeled as SQL
    return Interfaces.Item(id,bon_name,price,manufacturer,color,details,size,tax,1)

#Save a Transaction and Return the ID
def SaveTransaction(Items):
    pos = []

    #Get Transaction ID
    #TODO Add user System
    execute("insert into transaction (personal, sale_date) VALUES ('{}',now()) returning id, sale_date;".format("Max Musterman"))
    trans_id, sale_date = cur.fetchone()
    commit()
    for item in Items:
            #Create Position
            count = item.count
            execute("insert into position (product, count, total) VALUES ({},{},{}) returning id;"
                    .format( item.id,count, item.price * count))
            pos.append(cur.fetchone()[0])
            commit()
    for pos_id in pos:
        #Create Links
        execute("insert into transaction_position (pos, trans) VALUES ({},{});".format(pos_id,trans_id))
        commit()
    execute("update transaction set sale_date=now() where id={};".format(trans_id))
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
                .format(Barcode,id))
        commit()
    #Create the Internal Barcode:
    execute("insert into barcodes (barcode, item) values ('{}',{})"
            .format(f"LMR-{(id-1):04}" ,id))
    commit()

def GenerateTransactionExportSheet(id):
    logger.info("Generate Export far Salse after " + str(id))
    execute("SELECT extract(day  from transaction.sale_date) as \"Sale Day\"," +
       "extract(month  from transaction.sale_date) as \"Sale Month\"," +
       "extract(day  from now()) as \"Book Day\"," +
       "extract(month  from now()) as \"Book Month\"," +
       "concat('LMR Verkauf ID: ', transaction.id)," +
       "sum(position.total)," +
       "transaction.id " +
       "from transaction_position , position, transaction" +
        " where transaction_position.trans = transaction.id and transaction_position.pos = position.id" +
        " and transaction.id > {}".format(id) +
        " group by transaction.sale_date, transaction.id order by transaction.sale_date;")
    data = cur.fetchall()
    ReturnData = []
    for sale in data:
        ReturnData.append({
            "SaleID": sale[6],
            "SaleDay":sale[0],
            "SaleMonth":sale[1],
            "EntryDay":sale[2],
            "EntryMonth":sale[3],
            "Desc":sale[4],
            "Amount":sale[5]
        })
    return ReturnData

def GetTransactionData(id):
    execute("SELECT transaction.sale_date,position.count, coalesce(nullif(items.bon_name,''),items.name) ,position.total from position,transaction_position,items, transaction "+
    "where position.id =  transaction_position.pos and transaction.id = transaction_position.trans and items.id = position.product " +
    "and transaction_position.trans = {}".format(id))
    data = cur.fetchall()
    ReturnData = {
        "date":data[0][0],
        "id":id,
        "items":[]
    }
    logger.debug("Response form SQL:")
    logger.debug(data)
    for sale in data:
        ReturnData["items"].append({
            "name":sale[2],
            "cnt":sale[1],
            "price_per":sale[3] / sale[1]
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
