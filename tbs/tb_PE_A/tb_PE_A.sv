`timescale 1ns/1ns
module tb_PE_A();

  parameter accumulationPar=21;
  parameter weightPar=4;
  parameter activationPar=8;
  parameter barrelShifter_outPAr=15;

  logic clk;
  logic rst_n;
  logic weightLoad;
  logic [activationPar-1:0] activation;
  logic [weightPar-1:0] weight;
  logic [accumulationPar-1:0] inPartialSum;
  logic [accumulationPar-1:0] outPartialSum;
  logic [weightPar-1:0] out_weight;

  //DUT instance
  PE_A DUT(.*);

  //clock stimulus
  always #1 clk = ~clk;

  //rst_n stimulus
  initial begin
    rst_n = 0;
    clk = 0;
    @(posedge clk);
    rst_n = 1;
    weightLoad = 1'b1;
    activation = 8'b100;
    weight = 8'b10;
    inPartialSum=32'b1;
  end

endmodule