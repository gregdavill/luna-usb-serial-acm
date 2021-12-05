# This file is Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# License: BSD

import os

import litex
from migen import *

# Create a migen module to interface into a compiled nmigen module
class USBSerialDevice(Module):
    def __init__(self, platform, ulpi_pads):
        ulpi_data = TSTriple(8)

        reset = Signal()
        self.comb += ulpi_pads.rst.eq(~reset)
        
        vdir = os.path.join(os.getcwd(), "verilog")
        platform.add_source(os.path.join(vdir, f"LunaUSBSerialDevice.v"))


        self.usb_tx = usb_tx = litex.soc.interconnect.stream.Endpoint([("data", 8)])
        self.usb_rx = usb_rx = litex.soc.interconnect.stream.Endpoint([("data", 8)])

        self.specials += ulpi_data.get_tristate(ulpi_pads.data)

        self.params = dict(
            # Clock / Reset
            i_clk_usb   = ClockSignal("usb"),
            i_clk_sync   = ClockSignal("usb"),
            i_rst_sync   = ResetSignal(),

            o_ulpi__data__o = ulpi_data.o,
            o_ulpi__data__oe = ulpi_data.oe,
            i_ulpi__data__i = ulpi_data.i,
            o_ulpi__clk__o = ulpi_pads.clk,
            o_ulpi__stp = ulpi_pads.stp,
            i_ulpi__nxt__i = ulpi_pads.nxt,
            i_ulpi__dir__i = ulpi_pads.dir,
            o_ulpi__rst = reset, 

            # Tx stream (Data out to computer)
            o_tx__ready = usb_tx.ready,
            i_tx__valid = usb_tx.valid,
            i_tx__first = usb_tx.first,
            i_tx__last = usb_tx.last,
            i_tx__payload = usb_tx.data,
            
            # Rx Stream (Data in from a Computer)
            i_rx__ready = usb_rx.ready,
            o_rx__valid = usb_rx.valid,
            o_rx__first = usb_rx.first,
            o_rx__last = usb_rx.last,
            o_rx__payload = usb_rx.data,
        )

        self.specials += Instance("LunaUSBSerialDevice",
            **self.params
        )

        
