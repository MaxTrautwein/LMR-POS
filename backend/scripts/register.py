from os.path import exists
from Interfaces import Item


# Exceptions
class TransmitError(Exception):
    pass


class PathError(Exception):
    pass


class ConfigError(Exception):
    msg: str

    def __int__(self, msg: str):
        self.msg = msg


def to_hex(value: int | str):
    # for integers
    if type(value) == int:
        return f"{value:02x}"
    # for strings
    return value.encode('utf-8').hex()


class Register:
    tty: str

    # init new register
    def __init__(self, tty: str = '/dev/null'):
        # set local tty path
        if not exists(tty):
            raise PathError
        self._tty = tty

    # transmit hex string to register
    def _transmit(self, data: str):
        # check for successful transmit
        try:
            with open(self._tty, "wb") as file:
                # send converted string
                file.write(bytearray.fromhex(data.strip(' ')))
        except (Exception,):
            raise TransmitError

    # reset register to predefined values
    def _reset(self):
        # reset
        self._transmit('10 05 40')

        # TODO: set default config

    def _feed(self, n: int = 1):
        # check for valid configuration
        if n not in range(256):
            raise ConfigError('Can only feed lines in range(0, 256)')

        self._transmit('1B 64 ' + to_hex(n))

    def _cut(self):
        self._transmit('1B 69')

    def open(self):
        pass

    def print(self, items: list[Item]):
        cart = ''
        total = 0
        # generate item string
        for item in items:
            # line length = 42 chars -> 3 margin, 9 cnt, 17 name, 10 price, 3 margin
            cart += to_hex('   ')
            cart += to_hex(f"{item.count:2} Stk.  ")
            cart += to_hex(f"{item.name:17}")
            cart += to_hex(f"{item.price * item.count:6.2f} Eur")
            cart += to_hex('   ')

            # increase cart value
            total += item.price * item.count

        self._transmit(
            # start flashing to memory
            '1D 3A 01'
            
            # centered Header
            '1B 61 01' +
            to_hex('LMR HS-Esslingen') + '0D' +
            to_hex('Flandernstrasse 106') + '0D' +
            to_hex('73732 Esslingen') + '0D' +
            to_hex(' ') + '0D' +
            to_hex('Mo - Fr zu Pausenzeiten') + '0D' +
            to_hex(' ') + '0D' +

            # item list
            cart +

            # total price
            to_hex('   --------------------------==========   ') +

            to_hex('                             ') +
            to_hex(f"{total:6.2f} Eur") +
            to_hex('   ') +

            # TODO: footer

            # footer
            '' +

            # end memory flashing
            '1D 3A' +
            # print flash
            '1D 5E 01'
        )

        # feed newlines to crate bottom margin
        self._feed(0)
        self._feed(8)

        # cut recipe
        self._cut()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._transmit('1B 67')
