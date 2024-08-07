import decimal

from models.BaseModel import BaseModel


class PseudoItem(BaseModel):
    def __init__(self, name: str, bonName: str, price: decimal.Decimal, tax: decimal.Decimal, tags: list[str]):
        self.name = name
        self.bonName = bonName
        self.price = price
        self.tax = tax
        self.tags = tags
