class Item:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

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


pencil = Item(1, 'Stift', 1.99, '', '', '', '', 1, 2)
folder = Item(1, 'Ordner', 0.99, '', '', '', '', 1, 3)
ruler = Item(1, 'Lineal', 2.99, '', '', '', '', 1, 1)
rubber = Item(1, 'Radierer', 3.99, '', '', '', '', 1, 4)



testitems: list[Item] = [
    pencil, folder, ruler, rubber
]