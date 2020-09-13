`timescale 1ns/1ns

function integer depth_par;
    parameter parallelism=8;
    input integer target;
    integer j,result;
    result=parallelism;
    for (j=0;j<target;j++)
        result=result+2**j;
    return result;    
endfunction

module tb_cBarrelShifter();
    parameter depth=3;
    parameter parallelism=8;
    logic [parallelism-1:0] in_data;
    logic [depth-1:0] control;
    logic [14:0] out_data;

  //DUT instance
  cBarrelShifter #(  .parallelism(parallelism),
                    .depth(depth)) DUT(.*);

  integer i;
  //rst_n stimulus
  initial begin
    in_data=8'b00000001;
    control=3'b000;
    
    for (i=0;i<2**depth;i++) begin
        #1 control=i;
    end
  end

endmodule

