//UNSIGNED MULTIPLIER
module multiplier (multiplier, multiplicand, product);
  parameter parallelism=8;
  parameter ARCH_TYPE=0;
  /*SELECT ARCH_TYPE IN MOSULE INSTANCE AS:
      0 : synthesizer choose
      1 : complete csa implmentation
      2 : row cutted implmentation*/

  input unsigned [parallelism-1:0] multiplier;
  input unsigned [parallelism-1:0] multiplicand;
  output unsigned [2*parallelism-1:0] product;

  logic unsigned [parallelism-1:0] pps    [parallelism-1:0];
  logic unsigned [parallelism-3:0] sums   [parallelism-2:0];
  logic unsigned [parallelism-2:0] carrys [parallelism-2:0];

  genvar i;
  generate
    if (ARCH_TYPE==0) //synthesizer choose
      assign product = multiplier*multiplicand;
    else if (ARCH_TYPE==1) //complete csa tree
      //generate partial products
      for (i=0;i<parallelism;i++) begin
        assign pps[i] = (multiplier[i]) ? multiplicand : 8'b0;
      end
      //building the tree
      assign product[0] = pps[0][0];
      csaRow #(parallelism-1) row1 (  .a(pps[0][parallelism-1:1]),
                                      .b(pps[1][parallelism-2:0]),
                                      .ci(7'b0),
                                      .s({sums[0],product[1]}),
                                      .co(carrys[0]));
      //make all the following lines exept for last carry adder!
      for (i=1;i<parallelism-1;i++) begin
        csaRow #(parallelism-1) row1 (  .a(pps[i+1][parallelism-2:0]),
                                        .b({pps[i][parallelism-1],sums[i-1][parallelism-3:0]}),
                                        .ci(carrys[i-1][parallelism-2:0]),
                                        .s({sums[i],product[i+1]}),
                                        .co(carrys[i]));
      end
      //adder for last row
      adder #(.parallelism(parallelism),
              .ARCH_TYPE(1)) rcaFinale (.add1({1'b0,pps[parallelism-1][parallelism-1],sums[parallelism-2]}),
                                        .add0({1'b0,carrys[parallelism-2]}),
                                        .carry_in(1'b0),
                                        .sum(product[2*parallelism-1:parallelism]));
    else if(ARCH_TYPE==2)
      //AUTO_PRINT
  endgenerate
endmodule //multiplier
