import asyncio
import logging
from datetime import datetime
import websockets

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        print('Got a Heartbeat!')
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        )
        
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """

    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect,
        '127.0.0.2',
        9000,
        subprotocols=['ocpp1.6']
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
