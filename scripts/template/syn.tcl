analyze -library WORK -format sverilog {~/syn_part1/src/adder.sv ~/syn_part1/src/csaRow.sv ~/syn_part1/src/fullAdder.sv ~/syn_part1/src/multiplier.sv ~/syn_part1/src/register.sv ~/syn_part1/src/PE.sv}
elaborate PE -architecture verilog -library WORK

create_clock -name "clock" -period 0 {clk}
set_dont_touch_network clock

# flatten hierarchy
ungroup -all -flatten

compile -exact_map
//AUTO_PRINT
quit
