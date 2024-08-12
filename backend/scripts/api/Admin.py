from main import app, getRegister
from flask import request, jsonify, render_template
import logging
import db


logger = logging.getLogger('LMR_Log')
# Handles Admin Tasks


# TODO: Need to completely redo that Logic
@app.route('/AddNewItem', methods=['POST'])
def AddNewItem():
    content = request.json
    # db.AddNewItem(content)
    # What if any should we return !?
    return jsonify(content)


@app.route('/OpenDrawer', methods=['POST'])
def OpenDrawer():
    logger.info("Used Open Drawer Command")
    getRegister().open()
    return {}


# TODO: Remove that Later --> move the Frontend Fully to Angular
@app.get('/AdminAccess')
def Get_AdminAccess():
    return render_template("AdminAccess.html")