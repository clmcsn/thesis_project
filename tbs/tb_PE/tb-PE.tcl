if {[info exists env(NO_GUI)]} {
    set sim_mode "no_gui"
    puts "sim_mode set no_gui"
} else {
    set sim_mode "gui"
}

#this is just an example for future improvements
if {$sim_mode == "no_gui"} {
    puts "Running in command line mode. No waveforms will be available."
} elseif {$sim_mode == "gui"} {
    puts "Running in GUI mode."
} else {
    puts "Error. Invalid environment variable NO_GUI"
    exit 1
}

vlib ../work

vlog -work ../work ../../../src/components/*.sv
vlog -work ../work ../../../src/PE/PE.sv
vlog -work ../work +define+NO_GUI=1 ../tb_PE.sv
vsim -c ../work.tb_PE

run -all
