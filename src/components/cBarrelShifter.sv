function integer depth_par;
    parameter parallelism=8;
    input integer target;
    integer j,result;
    result=parallelism;
    for (j=0;j<target;j++)
        result=result+2**j;
    return result;    
endfunction

module cBarrelShifter (in_data,control,out_data);
    parameter depth=1;
    parameter parallelism=8;
    input [parallelism-1:0] in_data;
    input [depth-1:0] control;
    output[14:0] out_data;

    logic signed [parallelism-1+2**depth:0] p_shift [depth-1:0];
    
    barrelShifterRow #( .depth(0),
                        .parallelism(parallelism)) bsr ( .in_data(in_data),
                                                        .control(control[0]),
                                                        .out_data(p_shift[0][parallelism:0]));
    genvar i;
    generate
        for (i=1;i<depth;i++) begin
            localparam integer par=depth_par(i);
            barrelShifterRow #( .depth(i),
                                .parallelism(par)) bsr (    .in_data(p_shift[i-1][par-1:0]),
                                                            .control(control[i]),
                                                            .out_data(p_shift[i][par-1+2**i:0]));

        end
    endgenerate
    assign out_data = p_shift[depth-1];
endmodule