import decimal

from models.BaseModel import BaseModel


class ExportItem(BaseModel):
    def __init__(self, name: str, cnt: int, price: decimal.Decimal, tax: decimal.Decimal):
        self.name = name
        self.cnt = cnt
        self.price = price
        self.tax = tax
