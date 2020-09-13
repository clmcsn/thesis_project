module barrelShifterRow (in_data,control,out_data);
    parameter depth;
    parameter parallelism;
    input [parallelism-1:0] in_data;
    input control;
    output[parallelism-1+2**depth:0] out_data;
    genvar k;
    generate
        for (k=0; k<parallelism+2**depth; k++) begin
            if (k<2**depth)
                assign out_data[k] = (~control) ? in_data[k] : 1'b0;
            else if (k<parallelism)
                assign out_data[k] = (~control) ? in_data[k] : in_data[k-2**depth];
            else 
                assign out_data[k] = (~control) ? in_data[parallelism-1] : in_data[k-2**depth];
        end
    endgenerate
endmodule