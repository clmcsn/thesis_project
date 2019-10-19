module fullAdder (a,b,ci,s,co);
  input a;
  input b;
  input ci;
  output s;
  output co;
  assign s=a^b^ci;
  assign co=(a & b)|(ci & (a^b));
endmodule //fullAdder
