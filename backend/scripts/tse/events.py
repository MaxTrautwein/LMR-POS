import json


class DN_Events:
    def __init__(self, EventName):
        self.eventName = EventName

    def ShouldHandle(self, EventName: str) -> bool:
        return EventName == self.eventName

    def Handle(self, eventMsg: json):
        print("WARNING EVENT NOT IMPLEMENTED")
        print(eventMsg)

class DeviceStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)