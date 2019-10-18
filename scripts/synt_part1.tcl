analyze -library WORK -format sverilog {/home/gmsarda/thesis/thesis_project/src/components/register.sv /home/gmsarda/thesis/thesis_project/src/components/multiplier.sv /home/gmsarda/thesis/thesis_project/src/components/adder.sv /home/gmsarda/thesis/thesis_project/src/part1/PE.sv}
elaborate PE -architecture verilog -library WORK
create_clock -name "clock" -period 5 {clk}
compile -extact_map
