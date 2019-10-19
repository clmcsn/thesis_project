module csaRow (a,b,ci,s,co);
  parameter parallelism=8;
  input [parallelism-1:0] a;
  input [parallelism-1:0] b;
  input [parallelism-1:0] ci;
  output [parallelism-1:0] s;
  output [parallelism-1:0] co;

  genvar i;
  generate
      for (i=0; i<parallelism; i++) begin
          fullAdder fh (
            .a(a[i]),
            .b(b[i]),
            .ci(ci[i]),
            .s(s[i]),
            .co(co[i])
          );
      end
  endgenerate
endmodule //csaRow
