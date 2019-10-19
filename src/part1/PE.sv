module PE (activation,weight,inPartialSum,outPartialSum,clk,rst_n);
  parameter accumulationPar=32;
  parameter weightPar=8;
  input clk;
  input rst_n;
  input [weightPar-1:0] activation;
  input [weightPar-1:0] weight;
  input [accumulationPar-1:0] inPartialSum;
  output [accumulationPar-1:0] outPartialSum;

  //signals
  logic [weightPar-1:0] activationToMult;
  logic [weightPar-1:0] weightToMult;
  logic [2*weightPar-1:0] prodToAdd;
  logic [accumulationPar-1:0] pSumToAdd;
  logic [accumulationPar-1:0] addToOutput;

  register #(weightPar) activationRegister (  .parallelIn(activation),
                                                    .parallelOut(activationToMult),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));

  //weight register
  register #(weightPar) weightRegister (  .parallelIn(weight),
                                                    .parallelOut(weightToMult),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));
  //pSumRegister
  register #(accumulationPar) partialSumRegister (  .parallelIn(inPartialSum),
                                                    .parallelOut(pSumToAdd),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));
  //multiplier
  multiplier #( .parallelism(weightPar),
                .ARCH_TYPE(0)) mult ( .multiplier(weightToMult),
                                 .multiplicand(activationToMult),
                                 .product(prodToAdd));
  //adder
  adder #(accumulationPar) add (.add1(pSumToAdd),
                                .add0({{accumulationPar-2*weightPar{prodToAdd[2*weightPar-1]}},prodToAdd}),
                                .carry_in(1'b0),
                                .sum(addToOutput));

  //pSumRegister
  register #(accumulationPar) outPartialSumRegister (  .parallelIn(addToOutput),
                                                    .parallelOut(outPartialSum),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));

endmodule //PE
