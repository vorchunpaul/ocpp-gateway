import asyncio
import logging
from datetime import datetime
from typing_extensions import Self
from urllib import response
import websockets

from ocpp.routing import on as v201_on
from ocpp.v201 import ChargePoint as v201_cp_server
from ocpp.v201 import call_result as v201_call_result

from ocpp.v16 import call as v16_call
from ocpp.v16 import ChargePoint as v16_cp
from ocpp.v16.enums import RegistrationStatus as v16_RegistrationStatus

logging.basicConfig(level=logging.INFO)


class v16_point(v16_cp):    
    async def send_boot_notification(self):
        request = v16_call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response = await self.call(request)

        return response
            
async def create_v16_point(adr: str) -> v16_point:
    async with websockets.connect(
        adr,
        subprotocols=['ocpp1.6']
    ) as ws:
        cp = v16_point('CP_1', ws)
        print('Create CP16')
        return cp


class Gateway201_16(v201_cp_server):
    
    async def __init__(self, id, connection, response_timeout=30):
        super().__init__(id, connection, response_timeout)
        self.cp = await create_v16_point('ws://127.0.0.2:9000/CP_1')
    
    @v201_on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):       
        
        response = await self.cp.send_boot_notification()
        
        print (response)
        
        return v201_call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )
    
    
async def v201_server_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """

    charge_point_id = path.strip('/')
    charge_point = Gateway201_16(charge_point_id, websocket)

    await charge_point.start()
    
async def run_v201_server(ip: str):
    server = await websockets.serve(
        v201_server_connect,
        ip,
        9000,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("Start v201 server ...")
    await server.wait_closed()
