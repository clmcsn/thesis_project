`timescale 1ns/1ns
module tb_PE();

  parameter accumulationPar=32;
  parameter weightPar=8;
  logic clk;
  logic rst_n;
  logic [weightPar-1:0] activation;
  logic [weightPar-1:0] weight;
  logic [accumulationPar-1:0] inPartialSum;
  logic [accumulationPar-1:0] outPartialSum;

  //DUT instance
  PE #(.accumulationPar(accumulationPar),
                .weightPar(weightPar)) DUT(.*);

  integer fin_pointer,fout_pointer;

  //clock stimulus
  always #1 clk = ~clk;

  //rst_n stimulus
  initial begin
    rst_n = 0;
    clk = 0;
    activation = 8'b0;
    weight = 8'b0;
    inPartialSum=32'b0;
    fin_pointer= $fopen("../tb_PE.txt","r");
      fout_pointer= $fopen("../HWresult_PE.txt","w");
    @(posedge clk);
    rst_n=1;
    @(posedge clk);
    while (! $feof(fin_pointer)) begin
      @(posedge clk);
      $fscanf(fin_pointer,"%b",activation);
      $fscanf(fin_pointer,"%b",weight);
      $fscanf(fin_pointer,"%b",inPartialSum);
      @(posedge clk);
      @(posedge clk);
      @(negedge clk);
      $fwrite(fout_pointer,"%b\n",outPartialSum);
    end
    $finish;
    $fclose(fin_pointer);
    $fclose(fout_pointer);
  end

endmodule
