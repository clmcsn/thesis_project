`timescale 1ns/1ns
module tb_rcaAdder();
  parameter parallelism=8;
  logic [parallelism-1:0] a;
  logic [parallelism-1:0] b;
  logic [parallelism-1:0] ci;
  logic [parallelism-1:0] s;
  logic [parallelism-1:0] co;

  //DUT instance
  adder #(parallelism) DUT(.*);

  //rst_n stimulus
  initial begin
    a=  8'b00101100;
    b=  8'b01011101;
    ci= 8'b00011000;
  end

endmodule
