import decimal


class Item:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    # Note Count is the Number for Sale NOT how many are in stock
    def __init__(self, item_id: int, name: str, price: decimal.Decimal, tax: decimal.Decimal, count: int):
        self.id = item_id
        self.name = name
        self.price = price
        self.tax = tax
        self.count = count

    def SetCount(self, cnt):
        self.count = cnt
