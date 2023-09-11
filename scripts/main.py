import time
import status
import monitoring
import signals
import db
# import register


# TODO: improve error handling


# TODO: finish Register


def init():
    monitoring.log(status.INFO, 'Starting LMR-Backend...', True)

    try:
        signals.start_signal_handler()
        db.init()
    except db.NetworkError:
        pass
    except signals.SignalError:
        pass
    except (Exception,):
        pass

    monitoring.log(status.OK, 'Started LMR-Backend', True)


def cleanup(exitcode=0):
    monitoring.log(status.INFO, 'Starting cleanup...', True)

    db.drop_connection()

    monitoring.log(status.OK, 'Finished cleanup', True)

    monitoring.log((status.OK if exitcode == 0 else status.FAIL), 'Exiting with code ' + str(exitcode), True)
    exit(exitcode)


def test():
    try:
        db.execute("SELECT name FROM items WHERE cnt <= 5 AND price <= '$1.00'")
        print(db.fetch())
    except db.ExecError:
        return
    except db.FetchError:
        return


if __name__ == '__main__':

    init()

    # test code
    test()

    mainloop = True
    while mainloop:
        try:
            time.sleep(1)
        except signals.Interrupt:
            cleanup()
        except (Exception,):
            monitoring.log(status.WARN, 'Unhandled interrupt')
