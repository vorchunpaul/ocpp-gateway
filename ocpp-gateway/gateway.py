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


class v201_server(v201_cp_server):
    @v201_on('BootNotification')
    def on_boot_notification(self, charging_station, reason, **kwargs):
        return v201_call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    @v201_on('Heartbeat')
    def on_heartbeat(self):
        print('Got a Heartbeat!')
        return v201_call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )
 
class v16_point(v16_cp):
    async def send_heartbeat(self, interval):
        request = v16_call.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)
            
    async def send_boot_notification(self):
        request = v16_call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response = await self.call(request)

        if response.status == v16_RegistrationStatus.accepted:
            print("Connected to central system.")
            await self.send_heartbeat(response.interval)       

async def v201_server_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """

    charge_point_id = path.strip('/')
    charge_point = v201_server(charge_point_id, websocket)

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

async def start_v16_point(adr: str):
    async with websockets.connect(
        adr,
        subprotocols=['ocpp1.6']
    ) as ws:

        cp = v16_point('CP_1', ws)
        print('create point')
        await asyncio.gather(cp.start(), cp.send_boot_notification())

async def main():
    v201_server = asyncio.create_task(run_v201_server('127.0.0.1'))
    v201_point  = asyncio.create_task(start_v16_point('ws://127.0.0.2:9000/CP_1'))
    await asyncio.wait([v201_server, v201_point])    


if __name__ == '__main__':
    asyncio.run(main())
