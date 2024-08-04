from models.BaseModel import BaseModel


class BasketPosition(BaseModel):
    def __init__(self, ItemID: int, cnt: int):
        self.ItemID = ItemID
        self.cnt = cnt

    def getItemID(self):
        return self.ItemID

    def getCNT(self):
        return self.cnt
