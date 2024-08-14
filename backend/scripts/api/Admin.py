from main import app, getRegister
import logging


logger = logging.getLogger('LMR_Log')
# Handles Admin Tasks


@app.route('/OpenDrawer', methods=['POST'])
def OpenDrawer():
    logger.info("Used Open Drawer Command")
    getRegister().open()
    return {}