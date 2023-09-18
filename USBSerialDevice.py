# This file is Copyright (c) 2023-2021 Greg Davill <greg.davill@gmail.com>
# License: BSD

import os

from migen import *
import litex
from litex.soc.interconnect import stream

# Create a migen module to interface into a compiled nmigen module
class USBSerialDevice(Module):
    def __init__(self, platform, ulpi_pads, stream_clockdomain="sys", usb_clockdomain="usb"):
        # Attach verilog block to module
        vdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verilog")
        platform.add_source(os.path.join(vdir, f"LunaUSBSerialDevice.v"))
        ulpi_data = TSTriple(8)

        # Active LOW reset signal
        reset = Signal()
        self.comb += ulpi_pads.rst.eq(~reset)

        # Stream interface in/out of logic
        self.usb_tx = stream.Endpoint([("data", 8)])
        self.usb_rx = stream.Endpoint([("data", 8)])

        # Add clock domain crossing FIFOs
        tx_cdc = stream.ClockDomainCrossing([("data", 8)], stream_clockdomain, usb_clockdomain)
        rx_cdc = stream.ClockDomainCrossing([("data", 8)], usb_clockdomain, stream_clockdomain)
        self.submodules += tx_cdc, rx_cdc
        self.comb += [
            tx_cdc.sink.connect(self.usb_tx),
            self.usb_rx.connect(rx_cdc.source)
        ]
        
        self.specials += ulpi_data.get_tristate(ulpi_pads.data)

        self.params = dict(
            # Clock / Reset
            i_clk_usb   = ClockSignal(usb_clockdomain),
            i_clk_sync   = ClockSignal(usb_clockdomain),
            i_rst_sync   = ResetSignal(usb_clockdomain),

            o_ulpi__data__o = ulpi_data.o,
            o_ulpi__data__oe = ulpi_data.oe,
            i_ulpi__data__i = ulpi_data.i,
            o_ulpi__clk__o = ulpi_pads.clk,
            o_ulpi__stp = ulpi_pads.stp,
            i_ulpi__nxt__i = ulpi_pads.nxt,
            i_ulpi__dir__i = ulpi_pads.dir,
            o_ulpi__rst = reset, 

            # Tx stream (Data out: USB device to computer)
            o_tx__ready = tx_cdc.source.ready,
            i_tx__valid = tx_cdc.source.valid,
            i_tx__first = tx_cdc.source.first,
            i_tx__last = tx_cdc.source.last,
            i_tx__payload = tx_cdc.source.data,
            
            # Rx Stream (Data in: From a Computer to USB Device)
            i_rx__ready = rx_cdc.sink.ready,
            o_rx__valid = rx_cdc.sink.valid,
            o_rx__first = rx_cdc.sink.first,
            o_rx__last = rx_cdc.sink.last,
            o_rx__payload = rx_cdc.sink.data,
        )

        self.specials += Instance("LunaUSBSerialDevice",
            **self.params
        )
