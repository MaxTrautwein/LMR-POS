import json


class DN_Events:
    def __init__(self, EventName):
        self.eventName = EventName

    def ShouldHandle(self, EventName: str) -> bool:
        return EventName == self.eventName

    def Handle(self, eventMsg: json):
        print("WARNING EVENT NOT IMPLEMENTED")
        print(eventMsg)


# TODO: Handle the Blocking in case of Not Ready
# Expose the current Status to the Operator
class DeviceStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('DeviceStatus')
        if status == "idle":
            # This is the Only case where the Device is in a Usable State
            # Usage must be Blocked if we are in any other State
            print("Device is idle")
        elif status == "error":
            print("error")
        elif status == "disconnected":
            print("disconnected")
        elif status == "connected":
            print("connected")
        elif status == "fwupdate":
            print("fwupdate")


# TODO: In the Doc there is a Whitespace in front of the "SelfTestStatus"
# like " SelfTestStatus"; Uncertain if that is a Mistake
# TODO: Handle the Blocking in case of Not Ready
# Expose the current Status to the Operator
class SelfTestStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('SelfTestStatus')
        if status == "idle":
            # This is the Only case where the Device is in a Usable State
            # Usage must be Blocked if we are in any other State
            print("Device is idle")
        elif status == "error":
            print("error")
        elif status == "needed":
            # ERROR in Web Service Config
            # Self Test needs to be Triggerd
            print("needed")
        elif status == "busy":
            print("busy")
        elif status == "n/a":
            print("n/a")


# TODO: Warn The User in case of nearfull
# Expose the current Status to the Operator
class MemoryStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('MemoryStatus')
        if status == "ok":
            print("ok")
        elif status == "nearfull":
            print("nearfull --> PREPARE EXPORT ASAP")
        elif status == "full":
            print("EXPORT NOW!! If unlucky Device already Bricked")
        elif status == "n/a":
            print("n/a")


# TODO: Warn The User in case of nearfull
# Expose the current Status to the Operator
class SignatureStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('SignatureStatus')
        if status == "ok":
            print("ok")
        elif status == "nearfull":
            print("nearfull --> PREPARE for new Stick")
        elif status == "full":
            print("New Stick NOW!! Dont forget DeInit, NO other Actions possible until replacement")
        elif status == "n/a":
            print("n/a")


# TODO: Warn The User in case of nearfull
# Expose the current Status to the Operator
class CertificateStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('CertificateStatus')
        if status == "ok":
            print("ok")
        elif status == "nearfull":
            print("nearfull --> PREPARE for new Stick")
        elif status == "full":
            print("New Stick NOW!! Dont forget DeInit, NO other Actions possible until replacement")
        elif status == "n/a":
            print("n/a")


# Expose the current Status to the Operator
class ExportStart(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# Expose the current Status to the Operator
class ExportProgress(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# Expose the current Status to the Operator
class ExportEnd(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: Block Actions until Completed
# Expose the current Status to the Operator
class PerformSelfTestStart(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: Act according to result
# Expose the current Status to the Operator
# TODO: In the Doc there is a Whitespace in front of the "PerformSelfTestEnd"
# like " PerformSelfTestEnd"; Uncertain if that is a Mistake
class PerformSelfTestEnd(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: Block Actions until Completed
# Expose the current Status to the Operator
class UpdateCryptoFirmwareStart(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: In the Doc there is a Whitespace in front of the "UpdateCryptoFirmwareProgress"
# like " UpdateCryptoFirmwareProgress"; Uncertain if that is a Mistake
# TODO: Block Actions until Completed
# Expose the current Status to the Operator
class UpdateCryptoFirmwareProgress(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: Block Actions until Completed
# Expose the current Status to the Operator
class UpdateCryptoFirmwareEnd(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)


# TODO: Block Actions if busy
# Expose the current Status to the Operator
class ExportRemoveStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('ExportRemoveStatus')
        if status == "idle":
            # Only Case where actions are Allowed
            print("Device is idle")
        else:
            print("Not Ready")


# TODO: Block Actions if busy
# Expose the current Status to the Operator
class ExportDataStatus(DN_Events):
    def __init__(self, EventName):
        DN_Events.__init__(self, EventName)

    def Handle(self, eventMsg: json):
        print(eventMsg)
        status = eventMsg.get('ExportDataStatus')
        if status == "idle":
            # Only Case where actions are Allowed
            print("Device is idle")
        else:
            print("Not Ready")
