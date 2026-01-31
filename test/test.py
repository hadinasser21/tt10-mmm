import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

def set_din_only(dut, bit):
    # Force all ui bits low except ui[0]
    # This avoids accidentally leaving other bits as X/1.
    dut.ui_in.value = (bit & 1)

def get_z(dut):
    return int(dut.uo_out[0].value)

def get_state_dbg(dut):
    # uo_out[2:1] shows state (we wired it in Verilog)
    # state[0] = uo_out[1], state[1] = uo_out[2]
    s0 = int(dut.uo_out[1].value)
    s1 = int(dut.uo_out[2].value)
    return (s1 << 1) | s0

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Moore 101 test (race-free)")

    # 10us clock period
    period_us = 10
    cocotb.start_soon(Clock(dut.clk, period_us, units="us").start())

    # Initialize
    dut.ena.value = 1
    dut.uio_in.value = 0
    set_din_only(dut, 0)

    # Apply reset (active-low)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Drive input safely BEFORE edge, then sample AFTER edge.
    # We drive at t = (period/2) BEFORE the next rising edge to avoid race.
    half_period = period_us / 2

    async def step(bit, label=""):
        # Wait half cycle so we are away from clock edge
        await Timer(half_period, units="us")
        set_din_only(dut, bit)

        # Now wait for the rising edge where the FSM samples din
        await RisingEdge(dut.clk)

        z = get_z(dut)
        st = get_state_dbg(dut)
        dut._log.info(f"{label} din={bit} -> state={st:02b} z={z}")
        return z, st

    # Stream: 1 0 1 0 1
    zs = []
    states = []

    z, st = await step(1, "b1")
    zs.append(z); states.append(st)

    z, st = await step(0, "b2")
    zs.append(z); states.append(st)

    z, st = await step(1, "b3")
    zs.append(z); states.append(st)

    z, st = await step(0, "b4")
    zs.append(z); states.append(st)

    z, st = await step(1, "b5")
    zs.append(z); states.append(st)

    # Expected behavior:
    # After bits 1,0,1 we should enter S3_101 => z=1 on that sample
    assert zs[0] == 0, f"After 1 expected z=0, got z={zs[0]}, state={states[0]:02b}"
    assert zs[1] == 0, f"After 10 expected z=0, got z={zs[1]}, state={states[1]:02b}"
    assert zs[2] == 1, f"After 101 expected z=1, got z={zs[2]}, state={states[2]:02b}"
    assert zs[3] == 0, f"After next bit expected z=0, got z={zs[3]}, state={states[3]:02b}"
    assert zs[4] == 1, f"After 101 again expected z=1, got z={zs[4]}, state={states[4]:02b}"
