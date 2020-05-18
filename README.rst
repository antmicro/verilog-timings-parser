Verilog timings parser - a tool for extracting timing data from Verilog files
=============================================================================

This is a tool for extracting data from Verilog's `specify` blocks and saving them to other timing formats (Liberty, SDF).

Installation
------------

To install the package, run:

    sudo python3 -m pip install git+https://github.com/antmicro/verilog-timings-parser

Example Usage
-------------

To extract the timings from `specify` block to Liberty file, run:

    verilog-timings-to-liberty verilog.v library-name out.lib

This will create an `out.lib` file with Liberty library called `library-name` and timings for modules from `verilog.v` file.
