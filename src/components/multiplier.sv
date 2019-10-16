//UNSIGNED MULTIPLIER
module multiplier (multiplier, multiplicand, product);
  parameter parallelism=8;
  input unsigned [parallelism-1:0] multiplier;
  input unsigned [parallelism-1:0] multiplicand;
  output unsigned [2*parallelism-1:0] product;

  logic unsigned [parallelism-1:0] temp_prod;
  assign product = temp_prod;

  always_comb begin
    temp_prod=multiplier*multiplicand;
  end
endmodule //multiplier
