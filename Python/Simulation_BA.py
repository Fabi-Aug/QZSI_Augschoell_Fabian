import math
import xmlrpc.client
import numpy as np
import pandas as pd

def run_plecs_simulation(model_name, parameters, host="localhost", port=1080):
    """Sendet Parameter an PLECS und startet die Simulation über XML-RPC."""
    url = f"http://{host}:{port}/RPC2"
    server = xmlrpc.client.ServerProxy(url)
    opts = {'ModelVars': parameters}
    return server.plecs.simulate(model_name, opts)

# --- 1. SYSTEMPARAMETER ---
P_n = 1000
V_in = 400
V_pp_rms = 400
f_sw = 90000.0   
f_g = 50.0      
R_L = (V_pp_rms ** 2) / P_n

# --- 2. BERECHNUNGEN: QUASI-Z-SOURCE INVERTER (qZSI) ---
f_st = f_sw * 2
T = 1 / f_st

v_ln = (V_pp_rms * math.sqrt(2)) / math.sqrt(3) 
G = (2 * v_ln) / V_in
I_in = P_n / V_in
M = G / ((math.sqrt(3) * G) - 1)
D = 1 - ((math.sqrt(3) * M) / 2)
B = 1 / (1 - (2 * D)) 

T0 = D * T
T1 = T - T0
m_val = T1 / (T1 - T0)

V_pn = B * V_in  
V_c1 = ((1 - D) / (1 - (2 * D))) * V_in
V_c2 = (D / (1 - (2 * D))) * V_in

T0_max = (2 - (math.sqrt(3) * M)) / f_st
r_c = 0.20
L_qZSI = ((m_val * V_in) / (I_in * r_c)) * 0.5 * T0_max

r_v = 0.01
C_qZSI = (I_in * T0_max) / (B * V_in * r_v)

# --- 3. BERECHNUNGEN: LCL-FILTER ---
V_DC = V_pn  

E_n = V_pp_rms / math.sqrt(3)
w_g = 2 * math.pi * f_g

Z_b = (E_n**2) / P_n
C_b = 1 / (w_g * Z_b)

V_f = E_n
I_max = (P_n * math.sqrt(2)) / (3 * V_f)

delta_I_L_max = 0.10 * I_max
L_1 = V_DC / (6 * f_sw * delta_I_L_max)

C_f_calc = 0.05 * C_b

k_a = 0.2
w_sw = 2 * math.pi * f_sw
L_2 = (math.sqrt(1 / (k_a**2)) + 1) / (C_f_calc * (w_sw**2))

w_res = math.sqrt((L_1 + L_2) / (L_1 * L_2 * C_f_calc))
R_f = 1 / (3 * C_f_calc * w_res)

# --- 4. PLECS ÜBERGABE ---
model_name = "QZSI_3P" 

plecs_params = {
    'V_in': V_in,
    'M': M,
    'D': D,
    'f_sw': f_sw,
    'C': C_qZSI,
    'L': L_qZSI,
    'R_d': R_f,
    'L_inv': L_1,
    'L_grid': L_2,
    'C_f': C_f_calc,
    'R_L': R_L
}

# --- 5. FREQUENZ-SWEEP & CSV EXPORT ---
f_sw_sweep = np.linspace(80000, 110000, 100)
L_q_list, C_q_list, L1_list, L2_list = [], [], [], []

for f in f_sw_sweep:
    f_st_s = f * 2
    T_s = 1 / f_st_s
    T0_s = D * T_s
    T1_s = T_s - T0_s
    m_val_s = T1_s / (T1_s - T0_s)
    T0_max_s = (2 - (math.sqrt(3) * M)) / f_st_s

    L_q_s = ((m_val_s * V_in) / (I_in * r_c)) * 0.5 * T0_max_s
    C_q_s = (I_in * T0_max_s) / (B * V_in * r_v)
    
    L_1_s = V_DC / (6 * f * delta_I_L_max)
    w_sw_s = 2 * math.pi * f
    L_2_s = (math.sqrt(1 / (k_a**2)) + 1) / (C_f_calc * (w_sw_s**2))

    L_q_list.append(L_q_s * 1000)
    C_q_list.append(C_q_s * 1e6)
    L1_list.append(L_1_s * 1000)
    L2_list.append(L_2_s * 1000)

C_f_list = [C_f_calc * 1e6] * len(f_sw_sweep) 

sweep_data = pd.DataFrame({
    'f_sw_Hz': f_sw_sweep,
    'L_qZSI_mH': L_q_list,
    'C_qZSI_uF': C_q_list,
    'L1_Inverter_mH': L1_list,
    'L2_Netz_mH': L2_list,
    'C_f_LCL_uF': C_f_list
})

sweep_data.to_csv('Frequenz_Sweep_Bauteile.csv', index=False)

# --- 6. SIMULATION STARTEN ---
run_plecs_simulation(model_name, plecs_params)

# --- 7. WIRKUNGSGRAD AUS CSV ---
csv_pfad_eta = r"C:/MCI_MECH_6/Bachelor/PLECS/Wirkungsgrad.csv"
daten_eta = np.genfromtxt(csv_pfad_eta, delimiter=',', skip_header=1)
mask_eta = (daten_eta[:, 0] >= 0.05) & (daten_eta[:, 0] <= 0.1)
eta_val = np.mean(daten_eta[mask_eta, 1])

if eta_val < 2.0:
    eta_val *= 100