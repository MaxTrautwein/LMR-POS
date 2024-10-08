import decimal

from models.BaseModel import BaseModel


class CartItem(BaseModel):

    # Note: renaming the "id" parameter will break the parsing of json
    def __init__(self, id: int, name: str, bonName: str, price: decimal.Decimal, tax: decimal.Decimal,
                 tags: list[str], cnt: int = 1):
        self.id = id
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

