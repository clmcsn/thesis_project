`timescale 1ns/1ns
module tb_csaMultiplier();
  parameter parallelism=8;
  logic [parallelism-1:0] multiplier;
  logic [parallelism-1:0] multiplicand;
  logic [2*parallelism-1:0] product;

  //DUT instance
  multiplier #(  .parallelism(parallelism),
            .ARCH_TYPE(1)) DUT(.*);

  //rst_n stimulus
  initial begin
    multiplier=  8'b00010001;
    multiplicand=  8'b00010001;
  end
endmodule
