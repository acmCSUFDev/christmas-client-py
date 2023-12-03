# SPDX-License-Identifier: GPL-3.0-or-later

import os
import asyncio
import math

import libacmchristmas

import numpy as np


async def main():
    tree = libacmchristmas.tree.TreeController(url=os.environ["TEST_URL"])
    await tree.connect()
    for n in range(20):
        tree.leds[n] = 0x888800 + 8*n
    await tree.update_manual()
    await asyncio.sleep(3)
    await tree.clear()
    await asyncio.sleep(3)
    img = np.array(object=[], dtype=np.uint8)
    for x in range(tree.ix):
        for y in range(tree.iy):
            c = math.floor(((x+y)/(tree.ix+tree.iy))*255)
            img = np.concatenate((img, np.array([c, c, c, 255], dtype=np.uint8)))
    await tree.update_image(img)
    
    
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())    
