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

  logic unsigned [parallelism-1:0] temp_prod;
  logic unsigned [parallelism-1:0] pps    [parallelism-1:0];
  logic unsigned [parallelism-3:0] sums   [parallelism-2:0];
  logic unsigned [parallelism-2:0] carrys [parallelism-2:0];

  assign product = temp_prod;

  generate
    if (ARCH_TYPE==0) //synthesizer choose
      always_comb begin
        temp_prod=multiplier*multiplicand;
      end
    else if (ARCH_TYPE==1) //complete csa tree
      genvar i;
      generate
        //generate partial products
        for (i=0;i<parallelism;i++) begin
          if (multiplier[i]==0) begin
            assign pps[i] = 8'b0;
          end else begin
            assign pps[i] = multiplicand;
          end
        end
        //building the tree
        assign product[0] = pps[0][0];
        csaRow #(parallelism-1) row1 (  .a(pps[0][parallelism-1:1]),
                                        .b(pps[1][parallelism-2:0]),
                                        .ci(8'b0),
                                        .s({sums[0],product[1]}),
                                        .co(carrys[0]));
        generate //make all the following lines!
          for (i=1;i<parallelism-1;i++)
            csaRow #(parallelism-1) row1 (  .a(pps[i+1][parallelism-2:0]),
                                            .b(sums[i-1][parallelism-3:0]),
                                            .ci(carry[i-1][parallelism-2:0]),
                                            .s({sums[i],product[i+1]}),
                                            .co(carrys[i]));
          end
        endgenerate
        
  endgenerate
endmodule //multiplier
