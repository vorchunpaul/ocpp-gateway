# ocpp-gateway (WIP)

## What it is? 

OCPP 2.0.1 to 1.6 gateway.

Base on this [project](https://github.com/mobilityhouse/ocpp)

## How to run (local)

Start charge server v1.6 
```
python CS160.py
```   
Start gateway 
```
python gateway_runner.py
```  
Start charge point v2.0.1 
```
python CP201.py
```  

All done work in 3 tty

## Supported messages

| status |    v160       | v201|
|---|--------------------|-------------------------|
| + | BootNotification   | BootNotification        | 
| + | Heartbeat          | Heartbeat               |
| - | StartTransaction   | RequestStartTransaction |
| - | StopTransaction    | RemoteStopTransaction   |
| + | StatusNotification | StatusNotification      |
| - | MeterValues        | MeterValues             |

### Planned

all :-)

## Arhetecture

### DefList 

`CP` - charging point  
`CS` - OCPP server

### Sheme

```
CP(v201) -> (CS(v201) <-> CP(v106)) -> CS(v106)
```

## LICENSE

MIT (c) 2022 Pavel Mihalsou