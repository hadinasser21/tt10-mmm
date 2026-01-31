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
    input  wire       ena,      // always 1 when powered
    input  wire       clk,      // clock
    input  wire       rst_n      // active-low reset
);

    // -------------------------
    // Input mapping
    // -------------------------
    wire din = ui_in[0];

    // -------------------------
    // Moore FSM states (iverilog-safe)
    // -------------------------
    localparam [1:0] S0_IDLE = 2'b00;
    localparam [1:0] S1_1    = 2'b01;
    localparam [1:0] S2_10   = 2'b10;
    localparam [1:0] S3_101  = 2'b11;

    reg [1:0] state, next_state;

    // -------------------------
    // Next-state logic
    // -------------------------
    always @(*) begin
        next_state = state;
        case (state)
            S0_IDLE: next_state = (din) ? S1_1   : S0_IDLE;
            S1_1:    next_state = (din) ? S1_1   : S2_10;
            S2_10:   next_state = (din) ? S3_101 : S0_IDLE;
            S3_101:  next_state = (din) ? S1_1   : S2_10;
            default: next_state = S0_IDLE;
        endcase
    end

    // -------------------------
    // State register
    // -------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= S0_IDLE;
        else
            state <= next_state;
    end

    // -------------------------
    // Moore output logic
    // -------------------------
    wire z = (state == S3_101);

    // -------------------------
    // Outputs
    // -------------------------
    assign uo_out[0] = z;

    // Debug: expose state bits (optional)
    assign uo_out[2:1] = state;

    // Unused outputs
    assign uo_out[7:3] = 5'b0;

    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Silence unused warnings
    wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule
