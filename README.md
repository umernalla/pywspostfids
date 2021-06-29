# Python Websocket API POST Example
## Summary

The purpose of this example is to show how to make an off-stream Post of a JSON-formatted market price instrument
to an ADS Server with WebSocket enabled. 

It can be used to post defined fields + value to a specified service and RIC.

Fields and intial values must be specified in ***fields.json*** file - located in the same working folder.   
Example content of fields.json file:  
*{  
	"BID":45.55,  
	"ASK":46.45,  
	"BIDSIZE":1000,  
	"ASKSIZE":1101,  
	"TRDPRC_1": 45.99,  
	"DSPLY_NAME":"Test RIC"  
}*  
**NOTE**: Numeric fields values must be specified **without** quotes "''"

Every 3 seconds, the example will post incremental values for the numeric and float type fields

This application is intended as basic usage example. Some of the design choices
were made to favor simplicity and readability over performance.

NOTE: The example must be run with Python3.6 or greater.

## Command Line Usage

```python post_fids.py [--host hostname ] [--port port] [--app_id appID] [--user user] [--service service] [--ric ric]```

e.g.:  
python post_fids.py --host ads1 --port 15000 --app_id 256 --user umer --service DIST_CACHE --ric TEST.TST


Pressing the CTRL+C buttons terminates any example.
## Compiling Source
### Windows/Linux/macOS
1. __Install Python__
    - Go to: <https://www.python.org/downloads/>
    - Select the __Download tile__ for the Python 3.6 or higher version
    - Run the downloaded `python-<version>` file and follow installation instructions
2. __Install libraries__
    - Run (in order):
      - `pip install requests`
      - `pip install websocket-client`
	    **The websocket-client should be version 1.1.0 or higher**
3. __Run examples__
    - Default Parameters are set as follows:
      - host = '127.0.0.1'
      - port = '15000'
      - user = 'root'
      - app_id = '256'
      - position = <local machine's hostname>
      - service = 'DIST_CACHE'
      - ric = 'TEST.RIC'
    - run `post_fids.py` with overrides e.g. provide your own ads host, servicename and ric:
      - `python post_fids.py --hostname <hostname> -service <servicename> -ric <ric>`
