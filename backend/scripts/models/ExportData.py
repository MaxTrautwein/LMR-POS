import decimal

from models.BaseModel import BaseModel
from models.ExportItem import ExportItem


class ExportData(BaseModel):
    def __init__(self, _id: int, saleDay: int, saleMonth: int, entryDay: int, entryMonth: int,
                 description: str, total: decimal.Decimal, tax: decimal.Decimal, saleDate: str, items: list[ExportItem]):
        self.id = _id
        self.saleDay = saleDay
        self.saleMonth = saleMonth
        self.entryDay = entryDay
        self.entryMonth = entryMonth
        self.description = description
        self.total = total
        self.tax = tax
        self.saleDate = saleDate
        self.items = items
        self.netto = round(total / (decimal.Decimal(1) + tax), 2)
        self.taxAmount = total - self.netto



