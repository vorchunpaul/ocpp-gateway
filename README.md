# ocpp-gateway (WIP)

## What it is? 

OCPP 2.0.1 to 1.6 gateway.

Base on this [project](https://github.com/mobilityhouse/ocpp)

## Supported messages
| status |    v160       | v201|
|---|--------------------|-------------------------|
| X | BootNotification   | BootNotification        | 
| X | StartTransaction   | RequestStartTransaction |
| X | StopTransaction    | RemoteStopTransaction   |
| X | StatusNotification | StatusNotification      |
| X | MeterValues        | MeterValues             |
| X | Heartbeat          | Heartbeat               |

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