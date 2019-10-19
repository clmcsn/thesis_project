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
  logic unsigned [parallelism-1:0] sums   [parallelism-1:0];
  logic unsigned [parallelism-1:0] carrys [parallelism-1:0];

  assign product = temp_prod;

  generate
    if (ARCH_TYPE==0) //synthesizer choose
      always_comb begin
        temp_prod=multiplier*multiplicand;
      end
    else if (ARCH_TYPE==1) //complete csa tree

endmodule //multiplier
