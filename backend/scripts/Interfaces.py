class Item:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    #Note Count is the Number for Sale NOT how many are in stock
    def __init__(self, item_id: int, name: str, price: float, manufacturer: str, color: str, details: str, size: str
                 , tax: float, count: int):
        self.id = item_id
        self.name = name
        self.price = price
        self.manufacturer = manufacturer
        self.color = color
        self.details = details.split(';')
        self.size = size
        self.tax = tax
        self.count = count
    
    def SetCount(self, cnt):
        self.count = cnt
