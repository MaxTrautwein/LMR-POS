import base64
import json
from Helpertypes import ProcessTyp, ProcessTypBon
from events import *
from errors import *

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
        self.events: list[DN_Events] = [
            DeviceStatus("DeviceStatus")
        ]

        self.TSE_Errors: list[DN_TSE_Error] = [
            # IMPORTANT
            DN_TSE_Error(-5001,"ERROR_RETRIEVE_LOG_MESSAGE_FAILED",
                         "The return value ERROR_RETRIEVE_LOG_MESSAGE_FAILED indicates that the retrieving"
                         " of the log message parts that have been created by Secure Element most recently failed"),
            # IMPORTANT
            DN_TSE_Error(-5002, "ERROR_STORAGE_FAILURE",
                         "The return value ERROR_STORAGE_FAILURE indicates that storing"
                         " of the log message in the storage failed"),
            # IMPORTANT
            DN_TSE_Error(-5003, "ERROR_UPDATE_TIME_FAILED"
                         , "The return value ERROR_UPDATE_TIME_FAILED indicates that the execution"
                           " of the Secure Element functionality for setting the time failed"),
            DN_TSE_Error(-5004, "ERROR_PARAMETER_MISMATCH"
                         , "The return value ERROR_PARAMETER_MISMATCH indicates that there"
                           " is a mismatch regarding the particular parameters that have been provided "
                           "in the context of the export of stored data"),
            DN_TSE_Error(-5005, "ERROR_ID_NOT_FOUND"
                         , "The return value ERROR_ID_NOT_FOUND indicates that no data has been found "
                           "for the provided clientID in the context of the export of stored data"),
            DN_TSE_Error(-5006, "ERROR_TRANSACTION_NUMBER_NOT_FOUND"
                         , "The return value ERROR_NO_DATA_AVAILABLE indicates that no data has been found"
                           " for the provided selection in the context of the export of stored data"),
            DN_TSE_Error(-5007, "ERROR_NO_DATA_AVAILABLE"
                         , "The return value ERROR_NO_DATA_AVAILABLE indicates that no data has been found "
                           "for the provided selection in the context of the export of stored data"),
            DN_TSE_Error(-5008, "ERROR_TOO_MANY_RECORDS"
                         , "The return value ERROR_TOO_MANY_RECORDS indicates that the amount of requested "
                           "records exceeds the passed value for the maximum number of records in the context of "
                           "the export of stored data"),
            # IMPORTANT
            DN_TSE_Error(-5009, "ERROR_START_TRANSACTION_FAILED"
                         , "The return value ERROR_START_TRANSACTION_FAILED indicates that the execution of "
                           "the Secure Element functionality to start a transaction failed"),
            DN_TSE_Error(-5010, "ERROR_UPDATE_TRANSACTION_FAILED"
                         , "The return value ERROR_UPDATE_TRANSACTION_FAILED indicates that the execution of "
                           "the Secure Element functionality for updating a transaction failed"),
            # IMPORTANT
            DN_TSE_Error(-5011, "ERROR_FINISH_TRANSACTION_FAILED"
                         , "The return value ERROR_FINISH_TRANSACTION_FAILED indicates that the execution of "
                           "the Secure Element functionality for finishing a transaction failed"),
            DN_TSE_Error(-5012, "ERROR_RESTORE_FAILED"
                         , "The return value ERROR_RESTORE_FAILED indicates that the restore process in "
                           "the context of a restoring from a backup in form of exported data failed"),
            DN_TSE_Error(-5013, "ERROR_STORING_INIT_DATA_FAILED"
                         , "The return value ERROR_STORING_INIT_DATA_FAILED indicates that the storing of the "
                           "initialization data during the commissioning of the "
                           "SE API by the application operator failed"),
            DN_TSE_Error(-5014, "ERROR_EXPORT_CERT_FAILED"
                         , "The return value ERROR_EXPORT_CERT_FAILED indicates the collection of "
                           "the certificates for the export failed"),
            DN_TSE_Error(-5015, "ERROR_NO_LOG_MESSAGE"
                         , "The return value ERROR_NO_LOG_MESSAGE indicates that no log message parts have "
                           "been found in the Secure Element"),
            # IMPORTANT
            DN_TSE_Error(-5016, "ERROR_READING_LOG_MESSAGE"
                         , "The return value ERROR_READING_LOG_MESSAGE indicates that the retrieving of the "
                           "log message parts that have been created from Secure Element most recently failed"),
            # IMPORTANT
            DN_TSE_Error(-5017, "ERROR_NO_TRANSACTION"
                         , "The return value ERROR_NO_TRANSACTION indicates that no transaction is known to "
                           "be open under the provided transaction number"),
            # IMPORTANT
            DN_TSE_Error(-5018, "ERROR_SE_API_NOT_INITIALIZED"
                         , "The return value ERROR_SE_API_NOT_INITIALIZED indicates that the "
                           "SE API has not been initialized"),
            # IMPORTANT
            DN_TSE_Error(-5019, "ERROR_TIME_NOT_SET"
                         , "The return value ERROR_TIME_NOT_SET indicates that the managed data/time in the "
                           "Secure Element has not been updated after the initialization of the SE API or a period of "
                           "absence of current for the Secure Element"),
            # IMPORTANT
            DN_TSE_Error(-5020, "ERROR_CERTIFICATE_EXPIRED"
                         , "The return value ERROR_CERTIFICATE_EXPIRED indicates that a SE API function "
                           "is invoked and the certificate with the public key for the verification of the appropriate "
                           "type of log messages is expired. Even if a certificate expired, the log message parts are "
                           "created by the Secure Element and stored by the SE API. In this case, the return value "
                           "ERROR_CERTIFICATE_EXPIRED is returned only after the data of the "
                           "log message has been stored."),
            # IMPORTANT
            DN_TSE_Error(-5021, "ERROR_SECURE_ELEMENT_DISABLED"
                         , "The return value ERROR_SECURE_ELEMENT_DISABLED indicates that SE API "
                           "functions are invoked although the Secure Element has been disabled"),
            # IMPORTANT
            DN_TSE_Error(-5022, "ERROR_USER_NOT_AUTHORIZED"
                         , "The return value ERROR_USER_NOT_AUTHORIZED indicates that the user who has "
                           "invoked a restricted SE API function is not authorized to execute this function"),
            # IMPORTANT
            DN_TSE_Error(-5023, "ERROR_USER_NOT_AUTHENTICATED"
                         , "The return value ERROR_USER_NOT_AUTHENTICATED indicates that the user who has "
                           "invoked a restricted SE API function has not the status 'authenticated'"),
            DN_TSE_Error(-5024, "ERROR_DESCRIPTION_NOT_SET_BY_MANUFACTURER"
                         , "The return value ERROR_DESCRIPTION_NOT_SET_BY_MANUFACTURER indicates that the "
                           "function initialize has been invoked without a value for the input parameter description "
                           "although the description of the SE API has not been set by the manufacturer"),
            DN_TSE_Error(-5025, "ERROR_DESCRIPTION_SET_BY_MANUFACTURER"
                         , "The return value ERROR_DESCRIPTION_SET_BY_MANUFACTURER indicates that the "
                           "function initialize has been invoked with a value for the input parameter description "
                           "although the description of the SE API has been set by the manufacturer."),
            # Could be Important
            DN_TSE_Error(-5026, "ERROR_EXPORT_SERIAL_NUMBERS_FAILED"
                         , "The return value ERROR_EXPORT_SERIAL_NUMBERS_FAILED indicates that the "
                           "collection of the serial number(s) failed"),
            DN_TSE_Error(-5027, "ERROR_GET_MAX_NUMBER_OF_CLIENTS_FAILED"
                         , "The return value ERROR_GET_MAX_NUMBER_OF_CLIENTS_FAILED indicates that the "
                           "determination of the maximum number of clients that could use the SE API "
                           "simultaneously failed"),
            DN_TSE_Error(-5028, "ERROR_GET_CURRENT_NUMBER_OF_CLIENTS_FAILED"
                         , "The return value ERROR_GET_CURRENT_NUMBER_OF_CLIENTS_FAILED indicates that the "
                           "determination of the current number of clients using the SE API failed"),
            DN_TSE_Error(-5029, "ERROR_GET_MAX_NUMBER_TRANSACTIONS_FAILED"
                         , "The return value ERROR_GET_MAX_NUMBER_TRANSACTIONS_FAILED indicates that the "
                           "determination of the maximum number of transactions that can be managed "
                           "simultaneously failed"),
            # IMPORTANT
            DN_TSE_Error(-5030, "ERROR_GET_CURRENT_NUMBER_OF_TRANSACTIONS_FAILED"
                         , "The return value ERROR_GET_CURRENT_NUMBER_OF_TRANSACTIONS_FAILED indicates "
                           "that the determination of the number of currently opened transactions failed"),
            DN_TSE_Error(-5031, "ERROR_GET_SUPPORTED_UPDATE_VARIANTS_FAILED"
                         , "The return value ERROR_GET_SUPPORTED_UPDATE_VARIANTS_FAILED is raised if the "
                           "identification of the supported variant(s) for updating transactions failed."),
            DN_TSE_Error(-5032, "ERROR_DELETE_STORED_DATA_FAILED"
                         , "The return value ERROR_DELETE_STORED_DATA_FAILED indicates that the deletion of "
                           "the data from the storage failed"),
            DN_TSE_Error(-5033, "ERROR_UNEXPORTED_STORED_DATA"
                         , "The return value ERROR_UNEXPORTED_STORED_DATA indicates that the deletion of "
                           "data from the storage failed because the storage contains data that has not been exported"),
            # IMPORTANT
            DN_TSE_Error(-5034, "ERROR_SIGNING_SYSTEM_OPERATION_DATA_FAILED"
                         , "The return value ERROR_SIGNING_SYSTEM_OPERATION_DATA_FAILED indicates that the "
                           "determination of the log message parts for the system operation data by the "
                           "Secure Element failed"),
            # IMPORTANT
            DN_TSE_Error(-5035, "ERROR_USER_ID_NOT_MANAGED"
                         , "The return value ERROR_USER_ID_NOT_MANAGED indicates that the passed userId "
                           "is not managed by the SE API"),
            # IMPORTANT
            DN_TSE_Error(-5036, "ERROR_USER_ID_NOT_AUTHENTICATED"
                         , "The return value ERROR_USER_ID_NOT_AUTHENTICATED indicates that the passed "
                           "userId has not the status authenticated"),
            # IMPORTANT (But not used by us)
            DN_TSE_Error(-5037, "ERROR_DISABLE_SECURE_ELEMENT_FAILED"
                         , "The return value ERROR_DISABLE_SECURE_ELEMENT_FAILED indicates that the "
                           "deactivation of the Secure Element failed")
        ]
        self.Errors: list[DN_Error] = [
            DN_Error(1, "JSON_CODE_COMMAND_UNKNOWN", "The sent command has a JSON syntax error"),
            DN_Error(2, "JSON_CODE_COMMAND_UNSUPPORTED", "the command is not supported."),
            DN_Error(3, "JSON_CODE_PARAMETER_MISSING", "A JSON command has been sent without a "
                                                       "designated required parameter"),
            DN_Error(4, "JSON_CODE_PARAMETER_INVALID", "A JSON command has been sent a designated "
                                                       "required parameter which has a wrong value"),
            DN_Error(5, "JSON_CODE_COMMAND_CANNOT_BE_PROCESSED",
                     "A JSON command canot be processed for several reasons. Tyically this is described in "
                     "the Desc (description) field"),
            DN_Error(8, "JSON_CODE_DEVICE_ERROR",
                     "The JSON command cannot be processed due to a device error "
                     "(TSE or USB stick in this case)"),
            DN_Error(9, "JSON_CODE_PARAMETER_INVALID_BASE64",
                     "A parameter of this JSON command should be base64 encoded but the content is not valid"),
            DN_Error(10, "JSON_CODE_ERROR_IN_EXPORT_REMOVE_MODE",
                     "The Webservice is in ExportRemove mode. That is, you need first to successfully send"
                     " the ExportRemove command either with ExportRemove parameter with value true – or if this is "
                     "no longer possible – with parameter false"),
            DN_Error(11, "JSON_CODE_ERROR_IN_SELFTEST_MODE", "TSE is in Selftest mode"),
            DN_Error(12, "JSON_CODE_ERROR_SELFTEST_REQUIRED",
                     "TSE needs a selftest, handled by FW errors and initiated by "
                     "the Web service (if configured)"),
            DN_Error(13, "JSON_CODE_ERROR_NO_DEFAULT_CLIENT_ID",
                     "no default client id has yet been set for this TCP/IP connection"),
            DN_Error(14, "JSON_CODE_ERROR_DEFAULT_CLIENT_ID_NOT_MAPPED",
                     "TSE ConnectBox only: the specified CLIENT ID is not specified in the "
                     "TSE ConnectBox mapping configuration"),
            DN_Error(15, "JSON_CODE_ERROR_IN_EXPORT_DATA_MODE", "TSE is in export data mode"),
            DN_Error(16, "JSON_CODE_WRITE_ERROR",
                     "the necessary write operation to the device "
                     "(TSE or USB stick in this case) could not be performed"),
            DN_Error(17, "JSON_CODE_WS_LOGIN_FAILED", "login for TSE Connect Box failed"),
            DN_Error(18, "JSON_CODE_NOT_ALLOWED", "the required operation could not be performed due to "
                                                  "invalid access priviledge. (Only when working with "
                                                  "configured Login/Logout procedure)"),
            DN_Error(19, "JSON_CODE_ERROR_CLIENT_NOT_REGISTERED",
                     "In a command a client ID is used which is not regisered.."),
            DN_Error(20, "JSON_CODE_ERROR_CRYPTOCARD_NOTFOUND",
                     "the crypto card in the USB stick is not accessible. Seems to be a hardware error."),
            # VERY IMPORTANT
            DN_Error(21, "JSON_CODE_MAX_PARALLEL_TRANSACTIONS_REACHED",
                     "The maximum of started transactions has been reached. Applications must not use more than "
                     "the maximum as given in the GetDeviceInfo answer in the parameter MaxNumberOfOpenTransactions "
                     "Finish any open transaction first with FinishTransaction"),
            DN_Error(22, "JSON_CODE_MAX_SIGNATURES_REACHED",
                     "The maximum of allowd signatures has been reached. The TSE is full. "
                     "You need urgentlich to exchange the TSE hardware"),
            DN_Error(23, "JSON_CODE_MAX_REGISTERED_CLIENTS_REACHED",
                     "The maximum of registered clients has been reached. Applications must not use more "
                     "than the maximum as given in the GetDeviceInfo answer in the parameter MaxNumberOfClients "
                     "Unregister first some unused POS clients with DeregisterClientID."),
            DN_Error(24, "JSON_CODE_ERROR_CLIENT_HAS_UNFINISHED_TRANSACTIONS",
                     "When unregistering a clientID the TSE found some transactions related to the "
                     "clientID still unfinished. Finish such open transaction first with FinishTransaction."),
            DN_Error(25, "JSON_CODE_ERROR_DEVICE_HAS_UNFINISHED_TRANSACTIONS",
                     "When deinitializing the TSE obviously some transactions are still unfinished. "
                     "Finish any open transaction first with FinishTransaction."),
            DN_Error(26, "JSON_CODE_ERROR_PARAMETER_USER_INVALID",
                     "the given User ID is invalid. Only Admin and TimeAdmin User is allowed."),
            DN_Error(27, "JSON_CODE_ERROR_PARAMETER_PASSWORD_INVALID",
                     "The transferred password does not fullfil the required format of password regarding length."),
            DN_Error(28, "JSON_CODE_ERROR_PARAMETER_PUK_INVALID",
                     "The transferred PUK does not fullfil the required format of password regarding length."),
            DN_Error(29, "JSON_CODE_ERROR_PARAMETER_USER_WRONG",
                     "The transferred user is not the right one."),
            DN_Error(30, "JSON_CODE_ERROR_PARAMETER_PASSWORD_WRONG",
                     "The transferred password is not the right one. This error may come "
                     "three times then the user is blocked."),
            DN_Error(31, "JSON_CODE_ERROR_PARAMETER_PUK_WRONG",
                     "The transferred PUK is not the right one. This error may come three times then the "
                     "PUK is blocked. You can no longer use operation where a Puk is required."),
            DN_Error(32, "JSON_CODE_ERROR_PARAMETER_USER_BLOCKED",
                     "The operation fails since the user is blocked - due to too many failed attempts to login."),
            DN_Error(33, "JSON_CODE_ERROR_PARAMETER_PUK_BLOCKED",
                     "The PUK is blocked. You can no longer use operation where a Puk is required."),
            DN_Error(34, "JSON_CODE_ERROR_PARAMETER_PASSWORD_SAME",
                     "When trying to change the password you did pass the same "
                     "password for the old one and the new one"),
            DN_Error(35, "JSON_CODE_ERROR_PARAMETER_PUK_SAME",
                     "When trying to change the PUK you did pass the same PUK for the old one and the new one"),
            DN_Error(40, "JSON_CODE_ERROR_FIRMWARE_UPDATE_ERROR",
                     "when trying to update the crypto card with a new firmware this error is "
                     "in case of a failure reported."),
            DN_Error(41, "JSON_CODE_ERROR_IN_FIRMWARE_UPDATE",
                     "the command could not be executed since currently a crypto "
                     "firmware update is running in background."),
        ]



    def on_open(self, ws):
        print("WebSocket opened")


    def on_message(self, ws, message):
        print("Message received")
        print(message)

        # Handle Events if Contained
        event = message.get("event")
        if event is not None:
            for eventHandler in self.events:
                if eventHandler.ShouldHandle(event):
                    eventHandler.Handle(message)



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
    def StartTransaction(self, process: ProcessTypBon, password: str) -> None:
        print("Starting Transaction")
        self.sendCommand("StartTransaction", {
            "ClientID": self.ClientID,
            # "Typ": str(process.name),
            "Password": base64.b64encode(password.encode('utf-8')).decode('utf-8')  #,
            # "Data": {"TODO": "A Json Object of the Data"}
        })

    # Note: According to dsfinv_k_v_2_4 for ProcessTypBon, UpdateTransaction SHALL NOT be used

    # Note: Data is limited to 16000 chars but I doubt we could ever crack that
    def FinishTransaction(self, process: ProcessTypBon, password: str, transactionID: int) -> None:
        print("Ending Transaction")
        self.sendCommand("FinishTransaction", {
            "ClientID": self.ClientID,
            "Typ": str(process.name),
            "Password": base64.b64encode(password.encode('utf-8')).decode('utf-8'),
            "Data": process.getData(),
            "TransactionNumber": transactionID
        })
