% Initialize the final rotary-cylinder electronic simulation.
% Parameters are extracted from the original project analysis script.
% The report specifies 10 uF for the low-pass filter; the saved analysis uses
% 1 uF. Keep the saved analysis value by default and expose it here explicitly.
R1 = 4.7e3;
C1 = 10e-6;
R2 = 4.7e3;
C2 = 1e-6;  % Set to 10e-6 to compare the report's stated filter value.

h_integrator = tf(1 / (R1 * C1), [1 0]);
h_filtru = tf(1, [R2 * C2 1]);
