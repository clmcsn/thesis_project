module PE (activation,weight,inPartialSum,outPartialSum,clk,rst_n);
  parameter accumulationPar=32;
  parameter weightPar=8;
  parameter SeM=1; //if activation and weights are given as Sign&Magnitude
  parameter ARCH_TYPE=0; //

  input clk;
  input rst_n;
  input [weightPar-1:0] activation;
  input [weightPar-1:0] weight;
  input [accumulationPar-1:0] inPartialSum;
  output [accumulationPar-1:0] outPartialSum;

  //signals
  logic [weightPar-1:0] internal_weight;
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
  //internal weight assignment
  assign internal_weight = weight;
  //weight register
  register #(weightPar) weightRegister (  .parallelIn(internal_weight),
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
  generate
    if (ARCH_TYPE==0) //separate adder and multiplier from different architectures
      //multiplier
      multiplier #( .parallelism(weightPar),
                    .ARCH_TYPE(3)) mult ( .multiplier(weightToMult),
                                    .multiplicand(activationToMult),
                                    .product(prodToAdd));
      
      generate //generate adder according to 2s complement or SEM 
        if (SeM) begin //it depends on the architecture, 2's or sign and magnitude
          adder #(accumulationPar) add (.add1(pSumToAdd),
                                        .add0({{accumulationPar-2*weightPar{prodToAdd[2*weightPar-1]}},prodToAdd}),
                                        .carry_in(prodToAdd[2*weightPar-1]),
                                        .sum(addToOutput));
        end else begin
          adder #(accumulationPar) add (.add1(pSumToAdd),
                                        .add0({{accumulationPar-2*weightPar{prodToAdd[2*weightPar-1]}},prodToAdd}),
                                        .carry_in(1'b0),
                                        .sum(addToOutput));
        end
      endgenerate
    else if (ARCH_TYPE=1) begin //collapsed MAC type A
      
    end
  endgenerate
  //pSumRegister
  register #(accumulationPar) outPartialSumRegister (  .parallelIn(addToOutput),
                                                      .parallelOut(outPartialSum),
                                                      .clk(clk),
                                                      .rst_n(rst_n),
                                                      .clear(1'b0),
                                                      .sample_en(1'b1));

endmodule //PE
