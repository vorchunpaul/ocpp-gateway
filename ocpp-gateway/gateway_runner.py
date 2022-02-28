from argparse import Action
import asyncio
import logging
from datetime import datetime
import websockets

from ocpp.routing import on as v201_on
from ocpp.v201 import ChargePoint as v201_cp_server
from ocpp.v201 import call_result as v201_call_result

from ocpp.v16 import call as v16_call
from ocpp.v16 import ChargePoint as v16_cp
from ocpp.v16.enums import RegistrationStatus as v16_RegistrationStatus

logging.basicConfig(level=logging.INFO)

class ChargePoint(v16_cp):
    
    async def send_heartbeat(self):
        request = v16_call.HeartbeatPayload()
        await self.call(request)

            
    async def send_boot_notification(self, name, vendor):
        request = v16_call.BootNotificationPayload(
            charge_point_model=name,
            charge_point_vendor=vendor
        )

        response = await self.call(request)

        if response.status == v16_RegistrationStatus.accepted:
            # print("Connected to CSv160")
            return response
            
    async def send_notification(self, kwargs):
        request = v16_call.StatusNotificationPayload(
            connector_id=kwargs['connector_id'],
            error_code="NoError",
            status=kwargs['connector_status'],
        )
        
        await self.call(request)
        
        
class Gateway(v201_cp_server):
    
        
    @v201_on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        
        cp_boot = asyncio.create_task(self.cp.send_boot_notification(charging_station["model"], charging_station["vendor_name"]))
        a = await asyncio.gather(cp_boot)
        
        logging.debug(f"resv `BootNotification` from CPv201 {a}")
        
        return v201_call_result.BootNotificationPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
            interval=a[0].interval,
            status=a[0].status
        )

    @v201_on('Heartbeat')
    async def on_heartbeat(self):
        logging.info('resv `Heartbeat` from CPv201')
        
        cp_task = asyncio.create_task(self.cp.send_heartbeat())
        await asyncio.gather(cp_task)
        
        return v201_call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )
    
    @v201_on('StatusNotification')
    async def on_status_notificationt(self, **kwargs):
        logging.info(f'NOTIFICATION {kwargs}')
        
        cp_task = asyncio.create_task(self.cp.send_notification(kwargs))
        await asyncio.gather(cp_task)
        
        return v201_call_result.StatusNotificationPayload()

async def gateway_connect(cs_ws, path: str):
    cp_id = path.strip("/")
    
    logging.info('create ws to cp')
    cp_ws = await websockets.connect(
        f'ws://127.0.0.2:7000/{cp_id}',
        subprotocols=['ocpp1.6']
    )
    
    logging.info('connect cp')
    cp = ChargePoint(cp_id, cp_ws)
    cp_task = asyncio.create_task(cp.start())
    
    logging.info('create cs')
    gw = Gateway(cp_id, cs_ws, cp)
    gw_task = asyncio.create_task(gw.start())
    
    gw.cp = cp
    cp.gw = gw
    
    logging.info('start cp & server')
    await asyncio.gather(cp_task, gw_task)
    #gw = Gateway(cp_id, ws)
    
    
async def start_gw():
    
    async with websockets.serve(
        gateway_connect,
        '127.0.0.1',
        8000,
        subprotocols=['ocpp2.0.1']
    ) as ws:
        logging.info('GATEWAY START')
        await ws.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_gw())