## How it works
This project implements a Moore finite state machine (FSM) that detects the bit pattern **101** on input `din = ui[0]`.
The output `z = uo[0]` goes high **only** when the FSM is in the `S3_101` state (Moore output depends on state only).
Overlapping patterns are supported.

## How to test
Drive a serial bitstream into `din` and clock it.
Example: input `1,0,1` will cause `z` to become `1` once the FSM reaches the detect state.

## External hardware
None
