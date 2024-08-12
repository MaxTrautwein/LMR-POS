import decimal

from models.BaseModel import BaseModel


class SaleRecord(BaseModel):
    def __init__(self, _id: int, saleDay: int, saleMonth: int, entryDay: int, entryMonth: int,
                 description: str, total: decimal.Decimal, tax: decimal.Decimal):
        self.id = _id
        self.saleDay = saleDay
        self.saleMonth = saleMonth
        self.entryDay = entryDay
        self.entryMonth = entryMonth
        self.description = description
        self.total = total
        self.tax = tax

