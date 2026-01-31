import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def drive_din(dut, bit):
    # keep other ui bits 0, drive only ui[0]
    dut.ui_in.value = (bit & 1)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Moore 101 test")

    # Start clock (10 us period)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Helper: after each input bit is applied, wait 1 cycle then sample output
    async def step(bit):
        drive_din(dut, bit)
        await ClockCycles(dut.clk, 1)
        return int(dut.uo_out[0].value)

    # Bitstream with two detections (overlap-friendly)
    # Stream: 1 0 1 0 1
    # Detections should occur after the 3rd bit (first 101) and after 5th bit (second 101 overlapping)
    zs = []
    zs.append(await step(1))  # after "1"   -> z should be 0
    zs.append(await step(0))  # after "10"  -> z should be 0
    zs.append(await step(1))  # after "101" -> z should be 1
    zs.append(await step(0))  # continue    -> z should be 0 (Moore output depends on state)
    zs.append(await step(1))  # forms "101" again -> z should be 1

    assert zs[0] == 0
    assert zs[1] == 0
    assert zs[2] == 1
    assert zs[3] == 0
    assert zs[4] == 1
