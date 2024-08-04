import datetime
from os.path import exists
from Interfaces import Item
import time
import logging

logger = logging.getLogger('LMR_Log')


# Exceptions
class TransmitError(Exception):
    pass


class PathError(Exception):
    pass


class ConfigError(Exception):
    msg: str

    def __int__(self, msg: str):
        self.msg = msg


class IdError(ConfigError):
    pass


class NoItemsError(ConfigError):
    pass


class InconsistentTaxError(Exception):
    pass


def to_hex(value):
    # for integers
    if type(value) == int:
        return f"{value:02x}"
    # for strings
    return value.encode('utf-8').hex()


class Register:
    tty: str

    # init new register
    def __init__(self, tty: str = '/dev/null') -> None:
        # set local tty path
        if not exists(tty):
            raise PathError
        self._tty = tty
        self._reset()

    # transmit hex string to register
    def _transmit(self, data: str) -> None:
        # check for successful transmit
        try:
            with open(self._tty, "wb") as file:
                # send converted string
                file.write(bytearray.fromhex(data.strip(' ')))
        except (Exception,):
            raise TransmitError

    # reset register to predefined values
    def _reset(self) -> None:
        # reset
        self._transmit('10 05 40')

        # Do not lower Init time!
        time.sleep(3)

        # TODO: set default config

        self._transmit(
            # set barcode hri position to below
            '1D 48 02' +

            # cut recipe
            '1B 69'
        )

    def open(self) -> None:
        self._transmit('1B 70 00 64 32')

    # TODO Maybe add option to who made the Sale if User System is Implemented
    def print(self, items: list[Item], system_time: datetime.datetime, transaction_id: str = '00000000000') -> None:
        if len(transaction_id) != 11:
            raise IdError
        if not items:
            raise NoItemsError
        cart = ''
        total: float = 0
        tax: float = items[0].tax
        # generate item string
        for item in items:
            # check for correct tax rate
            if item.tax != tax:
                raise InconsistentTaxError
            taxFactor: float = 1.0 + tax
            taxPrecent = f"{int(tax * 100)}%"

            # line length = 42 chars -> 3 margin, 9 cnt, 17 name, 10 price, 3 margin
            cart += to_hex('   ')
            cart += to_hex(f"{item.count:2}x  ")
            cart += to_hex(f"{item.name:21.21}")
            cart += to_hex(f"{item.price:6.2f} Eur")
            cart += to_hex('   ') + '0D'

            # increase cart value
            total += float(item.price * item.count)

        self._transmit(
            # start flashing to memory
            '1D 3A 01'

            # centered Header
            '1B 61 01' +
            to_hex('LMR HS-Esslingen') + '0D' +
            to_hex('Flandernstrasse 101-1') + '0D' +
            to_hex('73732 Esslingen') + '0D' +
            to_hex(' ') + '0D' +
            to_hex('Mo - Fr zu Pausenzeiten') + '0D' +
            to_hex(' ') + '0D' +

            # item list
            cart +

            # total price
            to_hex(' ') + '0D' +
            to_hex('   --------------------------==========   ') + '0D' +

            to_hex('                     Gesamt: ') +
            to_hex(f"{total:6.2f} Eur") +
            to_hex('   ') + '0D' +

            # tax
            to_hex(' ') + '0D' +

            to_hex('   ------------------------------------   ') + '0D' +

            to_hex('   ') +
            to_hex(f"{'Netto ':26}") +
            to_hex(f"{total / taxFactor:6.2f} Eur") +
            to_hex('   ') + '0D' +

            to_hex('   ') +
            to_hex(f"{'MWST (' + taxPrecent + ')' :26}") +
            to_hex(f"{total - (total / taxFactor):6.2f} Eur") +
            to_hex('   ') + '0D' +

            to_hex('                             ----------   ') + '0D' +

            to_hex('   ') +
            to_hex(f"{'Brutto ':26}") +
            to_hex(f"{total:6.2f} Eur") +
            to_hex('   ') + '0D' +

            # TODO: zu zahlen / gegeben / Rückgeld ?

            # centered footer
            '1B 61 01' +
            # start barcode
            '1D 6B 00' +

            # barcode data
            to_hex(transaction_id) +

            # end barcode
            '00 00' + '0D' +

            to_hex(' ') + '0D' +

            # output date
            to_hex(system_time.strftime("%a, %d.%m.%Y, %H:%M:%S.%f")) +

            # end memory flashing
            '1D 3A' +
            # print flash
            '1D 5E 01' +

            # feed paper
            '1B 64 00 1B 64 08' +

            # cut recipe
            '1B 69'
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._transmit('1B 67')
