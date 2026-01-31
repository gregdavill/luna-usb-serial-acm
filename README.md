# Luna ACM

A LiteX module implementing a USB ACM module. 
Making use of the LUNA USB stack, compiled into verilog to include directly into LiteX SoCs.

## Building

To build the verilog USB core, install luna, and amaranth within your python enviroment.
Since upstream luna requires amaranth 0.5, using a virtial enviroment with venv is recommended.

Yosys is needed to produce the final verilog out, the amaranth-yosys pacakge is cross-platform, but can be skipped if yosys is already within your path.

```
python3 -m venv .venv
. ./.venv/bin/activate

pip3 install git+https://github.com/greatscottgadgets/luna.git
pip3 install amaranth-yosys
python3 build_verilog.py
```