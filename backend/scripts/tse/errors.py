class DN_TSE_Error(Exception):
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class DN_Error(Exception):
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
