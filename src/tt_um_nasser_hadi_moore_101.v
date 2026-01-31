/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_nasser_hadi_moore_101 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (1=output)
    input  wire       ena,      // always 1 when powered (can ignore)
    input  wire       clk,      // clock
    input  wire       rst_n      // active-low reset
);

    // --------- Pin mapping ----------
    wire din = ui_in[0];   // serial input
    // ui_in[1]..ui_in[7] unused

    // --------- Moore FSM states ----------
    typedef enum logic [1:0] {
        S0_IDLE = 2'b00,   // no match
        S1_1    = 2'b01,   // saw "1"
        S2_10   = 2'b10,   // saw "10"
        S3_101  = 2'b11    // saw "101"  => output z=1 (Moore)
    } state_t;

    state_t state, next_state;

    // Next-state logic (overlap allowed)
    always @(*) begin
        next_state = state;
        case (state)
            S0_IDLE: next_state = (din) ? S1_1  : S0_IDLE;
            S1_1:    next_state = (din) ? S1_1  : S2_10;     // "1" + 0 => "10"
            S2_10:   next_state = (din) ? S3_101: S0_IDLE;   // "10" + 1 => "101"
            S3_101:  next_state = (din) ? S1_1  : S2_10;     // overlap handling
            default: next_state = S0_IDLE;
        endcase
    end

    // State register with async active-low reset
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) state <= S0_IDLE;
        else        state <= next_state;
    end

    // Moore output (depends only on state)
    wire z = (state == S3_101);

    // --------- Outputs ----------
    assign uo_out[0] = z;

    // (Optional debug) expose state bits:
    assign uo_out[2:1] = state;   // uo_out[1]=state[0], uo_out[2]=state[1]

    // Unused outputs tied low
    assign uo_out[7:3] = 5'b0;

    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Prevent unused warnings (matches manual style)
    wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule
