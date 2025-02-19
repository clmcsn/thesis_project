`timescale 1ns/1ns
module tb_autoCsaMultiplier();
  parameter parallelism=8;
  logic [parallelism-1:0] multiplier;
  logic [parallelism-1:0] multiplicand;
  logic [2*parallelism-1:0] product;
  logic fake_clk;
  //DUT instance
  multiplier #(  .parallelism(parallelism),
            .ARCH_TYPE(2)) DUT(.*);

  integer fin_pointer,fout_pointer;

  always #1 fake_clk=~fake_clk;

  //rst_n stimulus
  `ifdef NO_GUI
    initial begin
      fake_clk=0;
      multiplier=  8'b0;
      multiplicand=  8'b0;
      fin_pointer= $fopen("../tb_autoCsaMultiplier.txt","r");
      fout_pointer= $fopen("../HWresult_autoCsaMultiplier.txt","w");
      while (! $feof(fin_pointer)) begin
        $fscanf(fin_pointer,"%b",multiplicand);
        $fscanf(fin_pointer,"%b",multiplier);
        @(posedge fake_clk);
        $fwrite(fout_pointer,"%b\n",product);
        @(posedge fake_clk);
      end
      $finish;
      $fclose(fin_pointer);
      $fclose(fout_pointer);
    end
  `else
    initial begin
      multiplier=  8'b00010001;
      multiplicand=  8'b00010001;
      @(posedge fake_clk);
      @(posedge fake_clk);
      $finish;
    end
  `endif
endmodule
