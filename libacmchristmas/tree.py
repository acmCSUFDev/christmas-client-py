# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import websockets
from google.protobuf.reflection import GeneratedProtocolMessageType
from PIL import Image

from . import christmas_pb2 as c
from . import image


class TreeController:
    def __init__(self, url: str):
        self.url = url
        self.ws = None
        self.ix = None  # image width
        self.iy = None  # image height
        self.leds = []

    async def connect(self) -> None:
        if self.ws is not None:
            await self.close()
        self.ws = await websockets.connect(self.url)
        res = (await self._send(c.GetLEDCanvasInfoRequest())).get_led_canvas_info
        self.ix, self.iy = res.width, res.height
        await self._cache_leds()

    async def close(self) -> None:
        if self.ws is None:
            return 
        await self.ws.close()
        self.ws = None
        self.ix = None
        self.iy = None
        self.leds = None

    async def update_image(self, img: np.array) -> None:
        assert img.dtype == np.uint8
        assert img.size == (self.ix * self.iy) * 4
        msg = c.SetLEDCanvasRequest()
        px = c.RGBAPixels()
        px.pixels = bytes(img)
        msg.pixels.CopyFrom(px)
        await self._send_lt(msg)
        await self._cache_leds()

    async def update_manual(self) -> None:
        if self.ws is None:
            raise PermissionError("You aren't connected, run .connect first")
        msg = c.SetLEDsRequest()
        msg.leds.extend(self.leds)
        await self._send_lt(msg)

    async def _send(self, msg: GeneratedProtocolMessageType) -> c.LEDServerMessage:
        await self._send_lt(msg)
        resp = c.LEDServerMessage()
        resp.ParseFromString(await self.ws.recv())
        if resp.error is not None and resp.error != "":
            raise PermissionError(f"Failure: {resp.error}")
        return resp

    # TODO: factor out _get_led_state()    

    async def _send_lt(self, msg: GeneratedProtocolMessageType) -> None:
        cmsg = c.LEDClientMessage()
        match type(msg):
            case c.GetLEDCanvasInfoRequest:
                cmsg.get_led_canvas_info.CopyFrom(msg)
            case c.SetLEDCanvasRequest:
                cmsg.set_led_canvas.CopyFrom(msg)
            case c.GetLEDsRequest:
                cmsg.get_leds.CopyFrom(msg)
            case c.SetLEDsRequest:
                cmsg.set_leds.CopyFrom(msg)
            case _:
                raise ValueError("Invalid message sent!")
        await self.ws.send(cmsg.SerializeToString())

    async def _cache_leds(self) -> None:
        self.leds = (await self._send(c.GetLEDsRequest())).get_leds.leds

    # Helpers
    # These functions are just around as user utilities

    async def clear(self) -> None:
        self.leds = [0 for _ in range(len(self.leds))]
        await self.update_manual()
        
    async def draw(self, img: Image) -> None:
        await self.update_image(image.load_direct(img, self.ix, self.iy))
        
    async def draw_from_file(self, path: str) -> None:
        await self.update_image(image.load_direct_from_disk(path, self.ix, self.iy))
