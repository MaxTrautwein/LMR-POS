from main import app
from flask import request
import logging
import db
from models import ExportData
from helpers import jsonify_response

logger = logging.getLogger('LMR_Log')
# Handles the Export of Purchases


@app.get('/Export')
@jsonify_response
def GetExport() -> list[ExportData.ExportData]:
    id = request.args.get('id')
    data = db.GenerateTransactionExportSheet(id)
    return data