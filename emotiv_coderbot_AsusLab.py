import requests
import json
import asyncio
import time
from websockets.sync.client import connect

client_Secret = ""

client_ID = ""


coderBot_1684 = ''

BASE_URL = coderBot_1684

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
        raise connectionError("check/restart connection from emotiv launcher app")
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

 


def streamRequest() -> list:

    
    
    message_streams = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "subscribe",
        "params": {
            "cortexToken": token(),
            "session": sessionID(),
            "streams": ['met']
            }
        }
    
    message_streams = json.dumps(message_streams)

    websocket.send(message_streams)

    message = websocket.recv()

    message = json.loads(message)

    cols = message['result']['success'][0]['cols']

    #data_stream = message['result']['success'][0]['streamName']


    return cols


def streamLoop(cols, stream_input):


    met_dict = {}
    met_list_values = []

    start = time.time()
        
    while True:
        
        message = websocket.recv()
        message = json.loads(message)
        met_list_values = message[stream_input]

        for i in range(len(met_list_values)):
            met_dict[cols[i]] = met_list_values[i]

        print(f": Subscription : {met_dict} \n")
        end = time.time()

        Eng = message['met'][1]
        Exc = message['met'][3]
        Lex = message['met'][4]
        Str = message['met'][6]
        Rel = message['met'][8]
        Int = message['met'][10]
        Foc = message['met'][12]

        if Eng is None:
            print("Nessun segnale. Controlla la qualità")
        else:
            if Eng > 0 and Exc > 0:
                move() # rimpiazzare con un programma di moto avanti
        
        length = end - start

        if length > 120: # il numero rappresenta il numero di secondi che deve durare l'esperimento
            break


    
        


def move():
    url = f"{BASE_URL}/control/move"
    data = {
        "speed": 100,  # Example speed
        "elapse": 1  # Example duration
    }
    response = requests.post(url, json=data)
    print(f"Move response: {response.status_code}\n")
    


def run_program():
    program_name = "move_forward"  # Replace with your program 

    url = f"{BASE_URL}/programs/{program_name}"
    response = requests.get(url)
    program_code = response.json().get("code")

    url = f"{BASE_URL}/programs/{program_name}/run"
    data = {
        "name": program_name,
        "code": program_code
    }
    response = requests.post(url, json=data)
    print(f"Run program response: {response.status_code}")




def main():


    userLogin()

    requestAccess()

    authorize()

    token()

    idheadset()

    streamLoop(streamRequest(), 'met')





        
        
if __name__ =='__main__':
    main()



