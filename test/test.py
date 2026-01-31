import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

def set_din_only(dut, bit):
    dut.ui_in.value = (bit & 1)

def get_z(dut):
    return int(dut.uo_out[0].value)

def get_state_dbg(dut):
    s0 = int(dut.uo_out[1].value)
    s1 = int(dut.uo_out[2].value)
    return (s1 << 1) | s0

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Moore 101 test (edge-aligned)")

    cocotb.start_soon(Clock(dut.clk, 10, units="us").start())

    dut.ena.value = 1
    dut.uio_in.value = 0
    set_din_only(dut, 0)

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # IMPORTANT:
    # Drive input on FALLING edge so it's stable before the next RISING edge.
    async def step(bit, label=""):
        await FallingEdge(dut.clk)
        set_din_only(dut, bit)
        await RisingEdge(dut.clk)

        z = get_z(dut)
        st = get_state_dbg(dut)
        dut._log.info(f"{label} din={bit} -> state={st:02b} z={z}")
        return z, st

    # Stream: 1 0 1 0 1
    zs = []
    states = []

    for i, b in enumerate([1, 0, 1, 0, 1], start=1):
        z, st = await step(b, f"b{i}")
        zs.append(z)
        states.append(st)

    # With proper edge alignment, detection occurs on b3 and b5
    assert zs[0] == 0, f"After 1 expected z=0, got z={zs[0]}, state={states[0]:02b}"
    assert zs[1] == 0, f"After 10 expected z=0, got z={zs[1]}, state={states[1]:02b}"
    assert zs[2] == 1, f"After 101 expected z=1, got z={zs[2]}, state={states[2]:02b}"
    assert zs[3] == 0, f"After next bit expected z=0, got z={zs[3]}, state={states[3]:02b}"
    assert zs[4] == 1, f"After 101 again expected z=1, got z={zs[4]}, state={states[4]:02b}"
