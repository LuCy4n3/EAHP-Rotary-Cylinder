% Run the final model without loading hardware or measurement scripts.
simulationDirectory = fileparts(mfilename('fullpath'));
run(fullfile(simulationDirectory, 'init_simulation.m'));
load_system(fullfile(simulationDirectory, 'eahpSIM.slx'));
simulation_result = sim('eahpSIM');
