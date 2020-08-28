`timescale 1ns/1ns
module tb_PE();

  parameter accumulationPar=32;
  parameter weightPar=8;
  logic clk;
  logic rst_n;
  logic [weightPar-1:0] activation;
  logic [weightPar-1:0] weight;
  logic [accumulationPar-1:0] inPartialSum;
  logic [accumulationPar-1:0] outPartialSum;

  //DUT instance
  PE #(.accumulationPar(accumulationPar),
                .weightPar(weightPar)) DUT(.*);

  //clock stimulus
  always #2 clk = ~clk;

  //rst_n stimulus
  initial begin
    rst_n=0;
    clk=0;
    @(posedge clk);
    rst_n=1;
    @(posedge clk);
    activation=-126;
    weight=-122;
    inPartialSum=-12;
  end

endmodule
