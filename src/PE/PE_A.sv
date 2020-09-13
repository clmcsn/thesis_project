module PE_A (activation,weight,out_weight,inPartialSum,outPartialSum,clk,rst_n,weightLoad);
  parameter accumulationPar=21;
  parameter weightPar=4;
  parameter activationPar=8;
  parameter barrelShifter_outPAr=15;

  input clk;
  input rst_n;
  input weightLoad;
  input [activationPar-1:0] activation;
  input [weightPar-1:0] weight;
  input [accumulationPar-1:0] inPartialSum;
  output [accumulationPar-1:0] outPartialSum;
  output [weightPar-1:0] out_weight;

  //signals
  logic [activationPar-1:0] activationToMult, xoredActivation;
  logic [weightPar-1:0] weightToMult, weightToStore;
  logic [barrelShifter_outPAr-1:0] prodToAdd; //not general line
  logic [accumulationPar-1:0] pSumToAdd;
  logic [accumulationPar-1:0] addToOutput;

  register #(activationPar) activationRegister (  .parallelIn(activation),
                                                    .parallelOut(activationToMult),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));

  //weight register
  register #(weightPar) weightRegister (  .parallelIn(weight),
                                                    .parallelOut(weightToStore),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));
  //weight register
  register #(weightPar) PeWeightRegister (  .parallelIn(weightToStore),
                                                    .parallelOut(weightToMult),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(weightLoad));

  //pSumRegister
  register #(accumulationPar) partialSumRegister (  .parallelIn(inPartialSum),
                                                    .parallelOut(pSumToAdd),
                                                    .clk(clk),
                                                    .rst_n(rst_n),
                                                    .clear(1'b0),
                                                    .sample_en(1'b1));
  //architecture here
  assign xoredActivation=activationToMult^{ $size(activationToMult){weight[weightPar-1]}};
  
  cBarrelShifter #( .depth(3),
                    .parallelism(activationPar)) barrelShifter(   .in_data(xoredActivation),
                                                                .control(weight[weightPar-2:0]), //we need to exclude the sign
                                                                .out_data(prodToAdd));
  
  adder #(accumulationPar) add (.add1(pSumToAdd),
                                .add0({{accumulationPar-barrelShifter_outPAr{prodToAdd[barrelShifter_outPAr-1]}},prodToAdd}),
                                .carry_in(weight[weightPar-1]),
                                .sum(addToOutput));

  register #(accumulationPar) outPartialSumRegister (  .parallelIn(addToOutput),
                                                      .parallelOut(outPartialSum),
                                                      .clk(clk),
                                                      .rst_n(rst_n),
                                                      .clear(1'b0),
                                                      .sample_en(1'b1));
  
  assign out_weight = weightToStore;

endmodule //PE