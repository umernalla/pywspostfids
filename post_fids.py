#|-----------------------------------------------------------------------------
#|            This source code is provided under the Apache 2.0 license      --
#|  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
#|                See the project's LICENSE.md for details.                  --
#|           Copyright (C) 2017-2020 Refinitiv. All rights reserved.         --
#|-----------------------------------------------------------------------------


#!/usr/bin/env python
""" Simple example of posting Market Price JSON data using Websockets """

import sys
import time
import getopt
import socket
import json
import websocket
import threading
import os
from threading import Thread, Event

# Global Default Variables
hostname = '127.0.0.1'
port = '15000'
user = 'root'
app_id = '256'
position = socket.gethostbyname(socket.gethostname())
service = 'DIST_CACHE'
ric = 'TEST.RIC'

# Global Variables
next_post_time = 0
web_socket_app = None
web_socket_open = False
post_id = 1
obj = None


def process_message(ws, message_json):
    """ Parse at high level and output JSON of message """
    message_type = message_json['Type']

    if message_type == "Refresh":
        if 'Domain' in message_json:
            message_domain = message_json['Domain']
            if message_domain == "Login":
                process_login_response(ws, message_json)
    elif message_type == "Ping":
        pong_json = { 'Type':'Pong' }
        ws.send(json.dumps(pong_json))
        print("SENT:")
        print(json.dumps(pong_json, sort_keys=True, indent=2, separators=(',', ':')))

    # If our Login stream is now open, we can start sending posts.
    global next_post_time
    if  ('ID' in message_json and message_json['ID'] == 1 and next_post_time == 0 and
            (not 'State' in message_json or message_json['State']['Stream'] == "Open" and message_json['State']['Data'] == "Ok")):
        next_post_time = time.time() + 3


def process_login_response(ws, message_json):
    """ Send post message """
    send_market_price_post(ws)

def send_market_price_post(ws):
    global post_id
    """ Send a post message containing market-price content for TRI.N """
    
    if post_id==1:
        msg_type = 'Refresh'
    else:
        msg_type = 'Update'
    
    mp_post_json = {
        'ID': 1,
        'Type':'Post',
        'Domain':'MarketPrice',
        'Key': {
            'Name': ric,
            'Service': service
        },
        'Ack':True,
        'PostID':post_id,
        'PostUserInfo': {
            'Address':position,  # Use IP address as the Post User Address.
            'UserID':os.getpid() # Use process ID as the Post User Id.
        },
        'Message': {
            'ID': 0,
            'Type':msg_type,
            'Domain':'MarketPrice',
            "Solicited": (post_id>1),
            'Fields': obj
        }
    }

    ws.send(json.dumps(mp_post_json))
    print("SENT:")
    print(json.dumps(mp_post_json, sort_keys=True, indent=2, separators=(',', ':')))
    post_id += 1
    
    for field in obj:
        if type(obj[field]) is float:
            obj[field]=round(obj[field]+0.1,2)
        elif type(obj[field]) is int:
            obj[field]+=1

def send_login_request(ws):
    """ Generate a login request from command line data (or defaults) and send """
    login_json = {
        'ID': 1,
        'Domain': 'Login',
        'Key': {
            'Name': '',
            'Elements': {
                'ApplicationId': '',
                'Position': ''
            }
        }
    }

    login_json['Key']['Name'] = user
    login_json['Key']['Elements']['ApplicationId'] = app_id
    login_json['Key']['Elements']['Position'] = position

    ws.send(json.dumps(login_json))
    print("SENT:")
    print(json.dumps(login_json, sort_keys=True, indent=2, separators=(',', ':')))


def on_message(ws, message):
    """ Called when message received, parse message into JSON for processing """
    print("RECEIVED: ")
    message_json = json.loads(message)
    print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))

    for singleMsg in message_json:
        process_message(ws, singleMsg)


def on_error(ws, error):
    """ Called when websocket error has occurred """
    print(error)


def on_close(ws):
    """ Called when websocket is closed """
    global web_socket_open
    print("WebSocket Closed")
    web_socket_open = False


def on_open(ws):
    """ Called when handshake is complete and websocket is open, send login """

    print("WebSocket successfully connected!")
    global web_socket_open
    web_socket_open = True
    send_login_request(ws)


if __name__ == "__main__":

    # Get command line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["help", "host=", "port=", "app_id=", "user=", "position=", "ric=", "service="])
    except getopt.GetoptError:
        print('Usage: market_price.py [--host hostname] [--port port] [--app_id app_id] [--user user] [--position position] [--ric ric_code] [--service service] [--help]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--help"):
            print('Usage: market_price.py [--hostname hostname] [--port port] [--app_id app_id] [--user user] [--position position] [--ric ric_code] [--service service] [--help]')
            sys.exit(0)
        elif opt in ("--hostname"):
            hostname = arg
        elif opt in ("--port"):
            port = arg
        elif opt in ("--app_id"):
            app_id = arg
        elif opt in ("--user"):
            user = arg
        elif opt in ("--position"):
            position = arg
        elif opt in ("--service"):
            service = arg
        elif opt in ("--ric"):
            ric = arg

    try:
        with open('fields.json', 'r') as myfile:
            data=myfile.read()
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        sys.exit(2)
        
    obj = json.loads(data)    
    
    # Start websocket handshake
    ws_address = "ws://{}:{}/WebSocket".format(hostname, port)
    print("Connecting to WebSocket " + ws_address + " ...")
    web_socket_app = websocket.WebSocketApp(ws_address, header=['User-Agent: Python'],
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close,
                                        subprotocols=['tr_json2'])
    web_socket_app.on_open = on_open

    # Event loop
    wst = threading.Thread(target=web_socket_app.run_forever)
    wst.start()

    try:
        while True:
            time.sleep(1)
            if next_post_time != 0 and time.time() > next_post_time:
                send_market_price_post(web_socket_app)
                next_post_time = time.time() + 3
    except KeyboardInterrupt:
        web_socket_app.close()
