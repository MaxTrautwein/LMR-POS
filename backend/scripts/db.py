import psycopg2
import monitoring
import status
import time


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
    monitoring.log(status.INFO, 'Attempting to connect to database...')
    # setup database connection
    for i in range(CONNECTION_RETRIES):
        try:
            con = psycopg2.connect(
                "dbname='inventory' user='lmr' host='localhost' password='lmrSecretDBPassword'")
            cur = con.cursor()
        except (Exception,):
            monitoring.log(status.WARN, 'Can\'t establish connection to database')
        else:
            monitoring.log(status.OK, 'Connected to database')
            return

        time.sleep(RETRY_TIMEOUT)
        monitoring.log(status.INFO, 'Reattempting to connect to database')

    monitoring.log(status.FAIL, 'Connection to database failed')
    raise NetworkError


def execute(cmd: str):
    try:
        cur.execute(cmd)
    except (Exception,):
        monitoring.log(status.WARN, 'DB can\'t exec: ' + cmd)
        if cur.closed:
            monitoring.log(status.WARN, 'database appears to be offline')
            init()
            monitoring.log(status.INFO, 'Retry DB exec: ' + cmd)
            execute(cmd)
        else:
            monitoring.log(status.FAIL, 'DB exec error')
            raise ExecError
    else:
        monitoring.log(status.INFO, 'DB exec: ' + cmd)


def fetch():
    try:
        response = cur.fetchall()
    except (Exception,):
        monitoring.log(status.WARN, 'DB can\'t fetch')
        if cur.closed:
            monitoring.log(status.WARN, 'database appears to be offline')
            init()
            monitoring.log(status.INFO, 'Retry DB fetch')
            response = fetch()
        else:
            monitoring.log(status.FAIL, 'DB fetch error')
            raise FetchError
    else:
        monitoring.log(status.INFO, 'DB fetch')
    return response


def commit():
    try:
        cur.commit()
    except (Exception,):
        monitoring.log(status.WARN, 'DB can\'t commit')
        if cur.closed:
            monitoring.log(status.WARN, 'database appears to be offline')
            init()
            monitoring.log(status.INFO, 'Retry DB commit')
            cur.commit()
        else:
            monitoring.log(status.FAIL, 'DB commit error')
            raise FetchError
    else:
        monitoring.log(status.INFO, 'DB commit')


def drop_connection():
    if con:
        monitoring.log(status.INFO, 'Closing database connection...')
        con.close()
        if con.closed:
            monitoring.log(status.OK, 'Closed database connection')
        else:
            monitoring.log(status.FAIL, 'Can\'t close database connection')
            monitoring.log(status.WARN, 'Leaving database connection open')
    else:
        monitoring.log(status.WARN, 'Skipping: Close database connection')
