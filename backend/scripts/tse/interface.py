import base64
import json
from Helpertypes import ProcessTyp, ProcessTypBon

import websocket
from queue import Queue


class DN_TSE:
    def __init__(self, webSocket="ws://localhost:10001", clientID="pos-1"):
        self.WebSocket = webSocket
        self.ClientID = clientID
        self.ws = websocket.WebSocketApp(webSocket,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close)

    def on_open(self, ws):
        print("WebSocket opened")

    def on_message(self, ws, message):
        print("Message received")
        print(message)

    # May need to look into ways to reconnect as we NEED that connection
    # Will be a problem if the Service closes the connection
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    # Actually Send a Message by wrapping it in STX & ETX as required
    def sendMessage(self, command: str) -> None:
        STX = '\x02'
        ETX = '\x03'
        self.ws.send(f"{STX}{command}{ETX}")

    # Interface for Sending a Command
    def sendCommand(self, command: str, options: dict) -> None:
        cmd = {"Command": command}
        cmd.update(options)
        self.ws.send(json.dumps(cmd))

    # Note According to dsfinv_k_v_2_4 Typ & Data MUST be Empty at StartTransaction
    # TODO: Check if we should omit them or send them as empty
    def StartTransaction(self, process: ProcessTypBon, password: str, data: any) -> None:
        print("Starting Transaction")
        self.sendCommand("StartTransaction", {
            "ClientID": self.ClientID,
            # "Typ": str(process.name),
            "Password": base64.b64encode(password.encode('utf-8')).decode('utf-8')  #,
            # "Data": {"TODO": "A Json Object of the Data"}
        })

    # Note: According to dsfinv_k_v_2_4 for ProcessTypBon, UpdateTransaction SHALL NOT be used

    # Note: Data is limited to 16000 chars but I doubt we could ever crack that
    def FinishTransaction(self, process: ProcessTypBon, password: str, data: any, transactionID: int) -> None:
        print("Ending Transaction")
        self.sendCommand("FinishTransaction", {
            "ClientID": self.ClientID,
            "Typ": str(process.name),
            "Password": base64.b64encode(password.encode('utf-8')).decode('utf-8'),
            "Data": process.getData(),
            "TransactionNumber": transactionID
        })
