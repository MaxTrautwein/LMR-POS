import datetime
import colors


# logging
def log(status, msg, bold=False):
    print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f"),
          status, (colors.BOLD if bold else '') + msg + colors.ENDC)
