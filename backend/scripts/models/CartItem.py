import decimal

from models.BaseModel import BaseModel


class CartItem(BaseModel):
    def __init__(self, _id: int, name: str, bonName: str, price: decimal.Decimal, tax: decimal.Decimal,
                 tags: list[str], cnt: int = 1):
        self.id = _id
        self.name = name
        self.bonName = bonName
        self.price = price
        self.tax = tax
        self.tags = tags
        self.cnt = cnt

    def getId(self):
        return self.id

    def getCnt(self):
        return self.cnt

