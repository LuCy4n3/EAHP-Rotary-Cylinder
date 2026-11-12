close all;
projectRoot = fileparts(fileparts(mfilename("fullpath")));
addpath(projectRoot);
data_id= readmatrix(fullfile(projectRoot, "data", "stepResponse", "values", "step_response_values_118", "complete_data.csv"), 'NumHeaderLines', 2);
data_valid= readmatrix(fullfile(projectRoot, "data", "stepResponse", "values", "step_response_values_119", "complete_data.csv"), 'NumHeaderLines', 2);
proces_out = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_129.csv"))
%spab_data = readmatrix("/PRBSresponse/values/prbs_response_values_018.csv", 'NumHeaderLines', 2);
datanou = readmatrix(fullfile(projectRoot, "data", "stepResponse", "batch_data_test_211.csv"),'NumHeaderLines',2);
% 210 la bucla deschisa bun
% 119 data valid real
% 118 data id real

%%
close all;

%147 proces out pt 0.5 ref si 10 s
%148 controller out pt ref 0.5 si 10 s
proces_out0_5 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_165.csv"),'NumHeaderLines', 2);
control_out0_5 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_164.csv"),'NumHeaderLines', 2);

%169 proces out pt 1 ref si 10 s
%168 controller out pt ref 1 si 10 s
proces_out1 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_169.csv"),'NumHeaderLines', 2);
control_out1 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_168.csv"),'NumHeaderLines', 2);

%150 proces out pt 2 ref si 10 s
%151 controller out pt 2 ref 10 s
proces_out2 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_171.csv"),'NumHeaderLines', 2);
control_out2 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_170.csv"),'NumHeaderLines', 2);
%152 proces out pt 2.5 ref si 10 s
%153 controller out pt 2.5 si 10 s
proces_out2_5 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_174.csv"),'NumHeaderLines', 2);
control_out2_5 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_172.csv"),'NumHeaderLines', 2);
%154 procesout pt 3.3 ref si 10 s
%155 controller pt 3.3 ref si 10 s
proces_out3_3 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_176.csv"),'NumHeaderLines', 2);
control_out3_3 = readmatrix(fullfile(projectRoot, "data", "stepResponse", "customRef", "custom_ref_test_175.csv"),'NumHeaderLines', 2);

tp0_5 = proces_out0_5(:,1);
yp0_5 = proces_out0_5(:,2);
rp0_5 = proces_out0_5(:,3);

tc0_5 = control_out0_5(:,1);
yc0_5 = control_out0_5(:,2);
rc0_5 = control_out0_5(:,3);

tp1 = proces_out1(:,1);
yp1 = proces_out1(:,2);
rp1 = proces_out1(:,3);

tc1 = control_out1(:,1);
yc1 = control_out1(:,2);
rc1 = control_out1(:,3);

tp2 = proces_out2(:,1);
yp2 = proces_out2(:,2);
rp2 = proces_out2(:,3);

tc2 = control_out2(:,1);
yc2 = control_out2(:,2);
rc2 = control_out2(:,3);

tp2_5 = proces_out2_5(:,1);
yp2_5 = proces_out2_5(:,2);
rp2_5 = proces_out2_5(:,3);

tc2_5 = control_out2_5(:,1);
yc2_5 = control_out2_5(:,2);
rc2_5 = control_out2_5(:,3);

tp3_3 = proces_out3_3(:,1);
yp3_3 = proces_out3_3(:,2);
rp3_3 = proces_out3_3(:,3);

tc3_3 = control_out3_3(:,1);
yc3_3 = control_out3_3(:,2);
rc3_3 = control_out3_3(:,3);


figure
subplot(5,2,1)
plot(tp1,[rp1 yp1])
title('Raspuns proces pentru referinta de 1V');
subplot(5,2,2)
plot(tc1,[rc1 yc1]);
title('Comanda controler pentru referinta 1V');
subplot(5,2,3)
plot(tp2,[rp2 yp2])
title('Raspuns proces pentru referinta de 2V');
subplot(5,2,4)
plot(tc2,[rc2 yc2])
title('Comanda controler pentru referinta de 2V');
subplot(5,2,5)
plot(tp2_5,[rp2_5 yp2_5])
title('Raspuns proces pentru referinta de 2.5V');
subplot(5,2,6)
plot(tc2_5,[rc2_5 yc2_5])
title('Comanda controler pentru referinta de 2.5V');
subplot(5,2,7)
plot(tp3_3,[rp3_3 yp3_3])
title('Raspuns proces pentru referinta de 3.3V');
subplot(5,2,8)
plot(tc3_3,[rc3_3 yc3_3])
title('Comanda controler pentru referinta de 3.3V');
subplot(5,2,9)
plot(tp0_5,[rp0_5 yp0_5]);
title('Raspuns proces pentru referinta 0.5V');
subplot(5,2,10)
plot(tc0_5,[rc0_5 yc0_5])
title('Comanda controler pentru referinta de 0.5V');

%%
close all
%118 identificare
%119 validare

i1 = 38;
i2 = 113;
i3 = 161;

t_id=data_id(:,1);
y_id=data_id(:,2);
u_id=data_id(:,3)*2;
figure
plot(t_id,[u_id y_id]);
title('Proces pneumatic identificat')
t_valid=data_valid(:,1);
y_valid=data_valid(:,2);
u_valid=data_valid(:,3)*2;
figure
plot(t_valid,[u_valid y_valid]);
title('Date validare')
t_nou=datanou(:,1);
y_nou=datanou(:,2);
u_nou=datanou(:,3);
figure
plot(t_nou,[u_nou y_nou]);
title('Proces simulat electronic')
Ts = t_id(2) - t_id(1); % Sampling time
%%
data_id = iddata(y_id(i1:i2), u_id(i1:i2), Ts);
data_valid = iddata(y_valid(i1:i2), u_valid(i1:i2), Ts);

model = iv4(data_id, [2 1 0]);  % [nb nf nk] — model orders

figure
compare(data_valid, model)
title("Comapre pe OE")

np = 2;  % number of poles 4 8
nz = 1;  % number of zeros 4 8
nk = 0; % 1 1

sys_tf = tfest(data_id, np, nz, nk);
sys_tf = tf(sys_tf.Numerator,sys_tf.Denominator,'iodelay',sys_tf.IODelay);
[A,B,C,D] = tf2ss(sys_tf.Numerator{1},sys_tf.Denominator{1})

sys_ss = ss(A,B,C,D)

figure 
% (u_valid(2) - u_valid(1))/Ts
% [y_sim,t_sim] = lsim(sys_ss,u_valid,t_valid,[u_valid(1) (u_valid(2) - u_valid(1))/Ts]);
% plot(t_sim,[y_sim y_valid]);
figure
compare(data_valid, sys_tf);
title("Compare pe tfest")
%%
% pentru un front crescator
numerator = [0.086497570485291,0.110584124642427];
denominator = [1,1.788302253458148e-04,0.370708683432494]
hp = tf(numerator,denominator,'iodelay',0);

cv = 1;
tr = 1;
sigma = 0.15;
wb = 2;

zeta = abs(log(sigma))/sqrt(pi^2+log(sigma)^2)
wn = 4/tr/zeta
cv = wn/2/zeta
wb = wn*sqrt(1 - 2*zeta^2 + sqrt(2 - 4*zeta^2 + 4*zeta^4))

hf = hp;
ho = tf(wn^2,[1 2*zeta*wn wn^2]);
hc = 1/hf*ho/(1-ho)
zpk(hc)
hd = hc*hf;
ho1 = hd/(1+hd);

figure
step(feedback(hf,1))
figure
step(ho1)
%%
figure
plot(t_spab,[u_spab ,y_spab])

id_data = iddata(y_spab,u_spab,0.01);
arx_spab = arx(id_data,[1,1,0]);

figure
step(tf(arx_spab.B,arx_spab.A,0.01))
i1 = 792
i2 = 815;
i3 = 821;
i4 = 853;
%%
close all
R1 = 20e3;
R2 = 20e3;
C1 = 100e-6;
C2 = 1e-6;

K1 = R1 * R2 * C1 * C2;   % 0.01
K2 = R1 * C2 + R2 * C2;   % 0.02

hp = tf([1], [K1 K2 1]);
figure
step(hp);
% Desired response
zeta = 0.5912;
Ts = 1.5;
wn = 4 / (zeta * Ts);     % ~4.51

% Desired characteristic equation:
ho = tf(wn^2,[1, 2*zeta*wn, wn^2]);  % s^2 + 5.33s + 20.34

hc = 1/hp*ho/(1-ho)
hcz1 = c2d(hc,50e-3,'zoh');
hcz = c2d(minreal(hc),50e-3,'zoh');
hcz.Variable = 'z^-1';
hc = minreal(hc);
hpz = c2d(hp,50e-3,'zoh');
hpz.Variable = 'z^-1';
t = 0:50e-3:10;

figure
step(2.7*feedback(hc*hp,1),t);
figure
step(feedback(hcz*hpz,1),t);
title('step resppnse descreter')
y = step(feedback(hcz*hpz,1),t);

c = zeros(length(t));

e = zeros(length(t));

e(1) = 1;
e(2) = 1 - y(2);
c(1) = 0.2035*e(1);
c(2) = 0.2035*e(2) - 0.3657*e(1) + 1.766*c(1);

for k = 3:length(t)
    e(k) = 1 - y(k);
    %c(k) = e(k)*0.01 - e(k-1)*0.01989+0.009911*e(k-2) +1.973*c(k-1) - 0.9737*c(k-2); % ?
    %c(k) = e(k)*0.2035 - e(k-1)*0.4047+0.2017*e(k-2) +1.974*c(k-1) - 0.9737*c(k-2); % 5ms
    %c(k) = e(k)*0.2035 - e(k-1)*0.3913+0.1998*e(k-2) +1.875*c(k-1) - 0.8752*c(k-2); % 25ms
    c(k) = e(k)*0.2035 - e(k-1)*0.3657+0.2069*e(k-2) +1.766*c(k-1)- 0.7659*c(k-2) ; % 50 ms ebuna
end

figure
%plot(t,[y c'])
stairs(t,c)
title('Closed-loop step response with PI controller (Guillemin-Truxal)')
%%
close all
R1 = 4.7e3;
C1 = 10e-6;
R2 = 4.7e3;
C2 = 1e-6;
h_filtru = tf(1,[R2*C2 1]);
h_integrator = tf([1/R1/C1],[1 0]);
t=0:0.001:4;
figure
step(2*h_integrator,t)
title('step intergrator')
figure
step(h_filtru,t)
title('filytru')
figure
hp=series(h_integrator,h_filtru)
step(2*hp,t)
title('proces')

%%
close all
hp_integraotr = hp*tf(1,[1 0])
ho = feedback(hp,1);
step(ho)
%rltool(ho)
ki = 44.78