//doesn't handle overflow case!!!
module adder (add1,add0,carry_in,sum);
  parameter parallelism=32;
  parameter ARCH_TYPE=0;
  /*SELECT ARCH_TYPE IN MOSULE INSTANCE AS:
      0 : synthesizer choose (default)
      1 : rca
  */
  input unsigned [parallelism-1:0] add1;
  input unsigned [parallelism-1:0] add0;
  input unsigned carry_in;
  output unsigned [parallelism-1:0] sum;
  logic unsigned [parallelism-1:0] temp_sum;
  logic unsigned [parallelism-2:0] carrys;
  assign sum = temp_sum;

  genvar i;
  generate
    if (ARCH_TYPE==0)
      assign temp_sum=add1+add0+carry_in;
    else if (ARCH_TYPE==1)
      fullAdder fh1 ( .a(add1[0]),
                      .b(add0[0]),
                      .ci(carry_in),
                      .s(temp_sum[0]),
                      .co(carrys[0]));
      for (i=1;i<parallelism-1;i++) begin
        fullAdder fhX ( .a(add1[i]),
                        .b(add0[i]),
                        .ci(carrys[i-1]),
                        .s(temp_sum[i]),
                        .co(carrys[i]));
      end
      fullAdder fh_last ( .a(add1[parallelism-1]),
                          .b(add0[parallelism-1]),
                          .ci(carrys[parallelism-2]),
                          .s(temp_sum[parallelism-1]),
                          .co());
  endgenerate
endmodule //adder
