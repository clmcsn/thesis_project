if {[info exists env(NO_GUI)]} {
    set sim_mode "no_gui"
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
if {$sim_mode == "gui"} {
  vlog -work ../work ../tb_autoCsaMultiplier.sv
} elseif {$sim_mode == "no_gui"} {
  vlog -work ../work +define+NO_GUI=1 ../tb_autoCsaMultiplier.sv
} else {
  puts "Error. Wrong envvironment variable"
}

run -all
