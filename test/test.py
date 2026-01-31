import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

def drive_din(dut, bit):
    # Drive only ui_in[0]; keep other bits 0
    dut.ui_in.value = (bit & 1)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Moore 101 test")

    # Start clock (10 us period)
    cocotb.start_soon(Clock(dut.clk, 10, units="us").start())

    # Init
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0

    # Reset (active low)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Moore-friendly step:
    # 1) apply input before clock edge
    # 2) wait for rising edge (state updates here)
    # 3) sample output after the edge
    async def step(bit):
        drive_din(dut, bit)
        await RisingEdge(dut.clk)
        return int(dut.uo_out[0].value)

    # Stream: 1 0 1 0 1
    # In this Moore FSM, z becomes 1 *after* the clock edge that transitions into S3_101.
    # With step() sampling after each edge, detections should appear on the 3rd and 5th samples.
    zs = []
    zs.append(await step(1))  # after seeing 1   -> 0
    zs.append(await step(0))  # after seeing 10  -> 0
    zs.append(await step(1))  # after seeing 101 -> 1 (now in detect state)
    zs.append(await step(0))  # next            -> 0
    zs.append(await step(1))  # detect again    -> 1

    assert zs[0] == 0
    assert zs[1] == 0
    assert zs[2] == 1
    assert zs[3] == 0
    assert zs[4] == 1
