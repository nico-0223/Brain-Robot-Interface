import json
import asyncio
import ssl
import time


from websockets.sync.client import connect

client_Secret = ""

client_ID = ""


try:
    websocket = connect("wss://localhost:6868")
except wssError:
    print("check wss requirements\n\n")

    
def userLogin() -> str :
    user_login_json = '{"id": 1,"jsonrpc": "2.0","method": "getUserLogin"}'
    websocket.send(user_login_json)
    user_login_message = websocket.recv()
    print (f"User Login: {user_login_message} \n\n")



def requestAccess() -> str:
    request_access_dict = {"id": 1,"jsonrpc": "2.0","method": "requestAccess","params": {"clientId": client_ID,"clientSecret": client_Secret}}
    request_access_json = json.dumps(request_access_dict)
    try:
        websocket.send(request_access_json)
        request_access_message = websocket.recv()
        print (f"Access granted\n\n")
    except:
        print (f"Error during access request: check app permission on Emotiv Launcher")


def authorize() -> str:
    authorize_dict = {"id": 1,"jsonrpc": "2.0","method": "authorize","params": {"clientId": client_ID,"clientSecret": client_Secret}}
    authorize_json = json.dumps(authorize_dict)
    websocket.send(authorize_json)
    authorize_message = websocket.recv()


    return authorize_message
        


def token() -> str:
    
    message_authorize_dict = json.loads(authorize())
    token = message_authorize_dict["result"]["cortexToken"]
    return token

def getLicense() -> str:

    send_license_dict = {
                     "id": 1,
                     "jsonrpc": "2.0",
                     "method": "getLicenseInfo",
                     "params": {
                                "cortexToken": token()
                                }
                    }

    send_license_json = json.dumps(send_license_dict)
    websocket.send(send_license_json)
    receive_license_json = websocket.recv()

    print (f"User License: {receive_license_json} \n\n")

    
    


def idheadset() -> str:
    message_idheadset = '{"id": 1,"jsonrpc": "2.0","method": "queryHeadsets"}'
    websocket.send(message_idheadset)
    message = websocket.recv()
    json_load = json.loads(message)
    idheadset = json_load["result"][0]["id"]
    
    
    return idheadset


def sessionID()-> str:
    
    message_createsession = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "createSession",
        "params": {
            "cortexToken": token(),
            "headset": idheadset(),
            "status": "open"
            }
        }
    
    message_createsession = json.dumps(message_createsession)
    websocket.send(message_createsession)
    message = websocket.recv()
    
    session_id = json.loads(message)
    if session_id["result"] == KeyError:
        raise connectionError("check/restart connection from app")
    session_id = session_id["result"]["id"]

    
    return session_id



def getRecord() :
    
    message_getrecord = {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "createRecord",
                    "params": {
                        "cortexToken": token(),
                        "session": session_ID(),
                        "title": "Cortex Record"
                                }
                        }
    
    message_getrecord = json.dumps(message_getrecord)
    websocket.send(message_getrecord)
    message = websocket.recv()

    record = json.loads(message)
    record = record["result"]

 


def send_StreamRequest(stream_input):

    
    
    message_streams = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "subscribe",
        "params": {
            "cortexToken": token(),
            "session": sessionID(),
            "streams": [stream_input]
            }
        }
    
    message_streams = json.dumps(message_streams)

    websocket.send(message_streams)

    message = websocket.recv()

    return message

    


def loop_Stream():

    for i in range(100):
        start = time.time()
        message = websocket.recv()
        #time.sleep(1)
        print(f"Subscription: {message} \n")
        end = time.time()
        length = end - start
        print("It took", length, "seconds!\n")
        

    




def main():
        
    stream_input = input("Available data stream: \n\n\n 'eeg' for EEG, 'met' for performance metrics, 'mot' for motion, 'dev' for device information, \n\n 'eq' for EEG quality, 'pow' for the power of EEG data, 'com' for mental command, \n\n 'fac' for facial expression, 'sys' for training of mental commands and facial expressions. \n\n\n Type requested data stream: ")

    print(stream_input)

    userLogin()

    requestAccess()

    authorize()

    getLicense()

    send_StreamRequest(stream_input)

    loop_Stream()

    

        
        
if __name__ =='__main__':
    main()









