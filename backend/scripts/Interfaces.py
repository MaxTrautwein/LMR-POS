class Item:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    #Note Count is the Number for Sale NOT how many are in stock
    def __init__(self, item_id: int, name: str, price: float, manufacturer: str, color: str, details: str, size: str
                 , tax: float, count: int, bon_name: str, cnt: int,min_cnt: int ):
        self.id = item_id
        self.name = name
        self.price = price
        self.manufacturer = manufacturer
        self.color = color
        self.details = details.split(';')
        self.size = size
        self.tax = tax
        self.count = count # NOT Part of the DB but used for Transactions
        self.bon_name = bon_name
        self.cnt = cnt
        self.min_cnt = min_cnt
    
    def __init__(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.price = json["price"]
        self.manufacturer = json["manufacturer"]
        self.color = json["color"]
        self.details = json["details"]
        self.size = json["size"]
        self.tax = json["tax"]
        self.count = json["count"] # NOT Part of the DB but used for Transactions
        self.bon_name = json["bon_name"]
        self.cnt = json["cnt"]
        self.min_cnt = json["min_cnt"]
    
    def GetBonName(self):
        if self.bon_name == '':
            return self.name
        return self.bon_name
    
    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "manufacturer": self.manufacturer,
            "color": self.color,
            "details":self.details,
            "size":self.size,
            "tax":self.tax,
            "count":self.count,
            "bon_name": self.bon_name,
            "cnt":self.cnt,
            "min_cnt":self.min_cnt
        }