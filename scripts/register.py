import monitoring
import status


# TTY_PATH = '/dev/ttyS0'
TTY_PATH = '/dev/null'


def send(cmd):
    try:
        with open(TTY_PATH, "wb") as file:
            file.write(bytearray.fromhex(cmd.strip(' ')))
    except (Exception,):
        monitoring.log(status.WARN, 'Register can\'t exec: ' + cmd)
    else:
        monitoring.log(status.INFO, 'Register exec: ' + cmd)


def expose_money():
    send('1B 70 00 64 32')


def feed_lines(n=3):
    send('1B 64 ' + f"{n:02}")


cut = ''
barcode = ''
