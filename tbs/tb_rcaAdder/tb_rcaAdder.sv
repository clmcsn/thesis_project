`timescale 1ns/1ns
module tb_rcaAdder();
  parameter parallelism=8;
  logic [parallelism-1:0] add1;
  logic [parallelism-1:0] add0;
  logic carry_in;
  logic [parallelism-1:0] sum;

  //DUT instance
  adder #(  .parallelism(parallelism),
            .ARCH_TYPE(1)) DUT(.*);

  //rst_n stimulus
  initial begin
    add0=  8'b00101100;
    add1=  8'b01011101;
    carry_in= 1'b0;
  end

endmodule
