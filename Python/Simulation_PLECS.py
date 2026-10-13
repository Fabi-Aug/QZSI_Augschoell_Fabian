import math
from plecs_interface import run_plecs_simulation
import matplotlib.pyplot as plt
import numpy as np

def get_user_value(name, default_val, unit):
    """Fragt den Benutzer nach einem Wert. Bei leerer Eingabe wird der Default-Wert genommen."""
    user_input = input(f"Wert für {name} in {unit} [Berechnet: {default_val:.6g}]: ").strip()
    if not user_input:
        return default_val
    try:
        return float(user_input)
    except ValueError:
        print(f"Ungültige Eingabe. Verwende berechneten Wert: {default_val:.6g} {unit}")
        return default_val

# --- 1. SYSTEMPARAMETER ---
P_n = 1000
V_in = 400
V_pp_rms = 400
f_sw = 90000.0   
f_g = 50.0      
R_L = (V_pp_rms ** 2) / P_n

# --- 1. SYSTEMPARAMETER (TEST-SETUP) ---
#P_n = 13.5         # Gesamtleistung für 9V an 6 Ohm
#V_pp_rms = 9.0     # Ziel-Ausgangsspannung (Phase-Phase)
#V_in = 10 #12.73
#f_sw = 90000.0   
#f_g = 50.0      
#R_L = (V_pp_rms ** 2) / P_n  # Ergibt exakt 6.0 Ohm

# --- 1. SYSTEMPARAMETER (TEST-SETUP) ---
#P_n = 36        
#V_pp_rms = 60     # Ziel-Ausgangsspannung(Phase-Phase)
#V_in =  85 
#f_sw = 90000.0   
#f_g = 50.0      
#R_L = (V_pp_rms ** 2) / P_n  # Ergibt exakt 6.0 Ohm


print("=" * 50)
print(" SYSTEMPARAMETER")
print("=" * 50)
print(f"P_n = {P_n} W | V_in = {V_in} V | V_pp_rms = {V_pp_rms} V")
print(f"f_sw = {f_sw/1000} kHz | f_g = {f_g} Hz | R_L = {R_L} Ohm\n")

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
V_DC = V_pn  # Übergabe der Spannung vom qZSI

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

print("=" * 50)
print(" BERECHNETE WERTE")
print("=" * 50)
print(f"M       : {M:.3f}")
print(f"D       : {D:.3f}")
print(f"C       : {C_qZSI:.9f} F")
print(f"L       : {L_qZSI:.6f} H")
print(f"L_inv   : {L_1:.6f} H")
print(f"L_grid  : {L_2:.9f} H")
print(f"C_f     : {C_f_calc:.9f} F")
print(f"R_d     : {R_f:.3f} Ohm\n")



# Name der PLECS-Datei ohne ".plecs"
#model_name = "QZSI_3P_ideal" 
model_name = "QZSI_3P" 

if model_name == "QZSI_3P":
    R_Li = 0.28 * 2
    R_Ci = 0.0395
    C_qZSI_chosen = 1e-6
    L_qZSI_chosen = 1.6e-3
    R_f_chosen = 0.56
    R_L_inv = 1.95
    R_L_grid = 0.048
    R_C_f = 0
    L_1_chosen = 8.2e-3
    L_2_chosen = 10e-6
    C_f_chosen = 3.3e-6

    print("=" * 50)
    print(" AUSGEWÄHLTE WERTE FÜR PLECS")
    print("=" * 50)
    print(f"C       : {C_qZSI_chosen:.9f} F")
    print(f"L       : {L_qZSI_chosen:.6f} H")
    print(f"L_inv   : {L_1_chosen:.6f} H")
    print(f"L_grid  : {L_2_chosen:.6f} H")
    print(f"C_f     : {C_f_chosen:.9f} F")
    print(f"R_d     : {R_f_chosen:.3f} Ohm\n")
    
    
    # --- 5. PLECS ÜBERGABE ---
    plecs_params = {
        'V_in': V_in,
        'M': M,
        'D': D,
        'f_sw': f_sw,
        'C': C_qZSI_chosen,
        'L': L_qZSI_chosen,
        'R_d': R_f_chosen,
        'L_inv': L_1_chosen,
        'L_grid': L_2_chosen,
        'C_f': C_f_chosen,
        'R_L_inv': R_L_inv,
        'R_L_grid': R_L_grid,
        'R_C_f': R_C_f,
        'R_L': R_L,
        'R_Li': R_Li,
        'R_Ci': R_Ci
    }
else:
    # --- 4. BENUTZERABFRAGE FÜR EIGENE BAUTEILWERTE ---
    print("=" * 50)
    print(" BAUTEILWERTE FÜR DIE SIMULATION")
    print("=" * 50)
    choice = input("Möchtest du eigene Bauteilwerte eingeben? (j/n) [Standard: n]: ").strip().lower()

    if choice == 'j' or choice == 'ja':
        print("\nGib deine gewünschten Werte ein (als Dezimalzahl oder z.B. 1.5e-6).")
        print("Drücke einfach Enter, um den berechneten Wert beizubehalten.\n")
        C_qZSI   = get_user_value("C (qZSI Kondensator)", C_qZSI, "F")
        L_qZSI   = get_user_value("L (qZSI Spule)", L_qZSI, "H")
        L_1      = get_user_value("L_inv (LCL Inverter-Spule)", L_1, "H")
        L_2      = get_user_value("L_grid (LCL Netz-Spule)", L_2, "H")
        C_f_calc = get_user_value("C_f (LCL Filterkondensator)", C_f_calc, "F")
        R_f      = get_user_value("R_d (LCL Dämpfungswiderstand)", R_f, "Ohm")
        print("\nNeue Werte übernommen!\n")
    else:
        print("Berechnete Werte werden für die Simulation verwendet.\n")
    # --- 5. PLECS ÜBERGABE ---
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
#=====================================================================



ENABLE_SWEEP_PLOT = False   # <--- HIER EIN- UND AUSSCHALTEN (True / False)

if ENABLE_SWEEP_PLOT:
    print("Erstelle Frequenz-Sweep Plot (80 kHz bis 110 kHz). Fenster schließen, um im Skript fortzufahren...")

    # Array mit Frequenzen von 80 kHz bis 110 kHz (100 Punkte)
    f_sw_sweep = np.linspace(80000, 110000, 100)

    # Listen zum Speichern der neu berechneten Bauteilwerte
    L_q_list = []
    C_q_list = []
    L1_list = []
    L2_list = []

    for f in f_sw_sweep:
        # Frequenzabhängige Variablen für den aktuellen Schritt (f) neu berechnen
        f_st_s = f * 2
        T_s = 1 / f_st_s
        T0_s = D * T_s
        T1_s = T_s - T0_s
        m_val_s = T1_s / (T1_s - T0_s)
        T0_max_s = (2 - (math.sqrt(3) * M)) / f_st_s

        # Bauteilwerte für aktuelle Frequenz berechnen
        L_q_s = ((m_val_s * V_in) / (I_in * r_c)) * 0.5 * T0_max_s
        C_q_s = (I_in * T0_max_s) / (B * V_in * r_v)
        
        L_1_s = V_DC / (6 * f * delta_I_L_max)
        w_sw_s = 2 * math.pi * f
        L_2_s = (math.sqrt(1 / (k_a**2)) + 1) / (C_f_calc * (w_sw_s**2))

        # In die Listen speichern (Umrechnung in mH und µF für eine schönere y-Achse)
        L_q_list.append(L_q_s * 1000)
        C_q_list.append(C_q_s * 1e6)
        L1_list.append(L_1_s * 1000)
        L2_list.append(L_2_s * 1000)

    # Plot erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot 1: Spulen (Induktivitäten)
    ax1.plot(f_sw_sweep / 1000, L_q_list, label='L_qZSI', color='#1f77b4', linewidth=2)
    ax1.plot(f_sw_sweep / 1000, L1_list, label='L_1 (Inverter)', color='#ff7f0e', linewidth=2)
    ax1.plot(f_sw_sweep / 1000, L2_list, label='L_2 (Netz)', color='#2ca02c', linewidth=2)
    ax1.set_title('Verkleinerung der Spulen')
    ax1.set_xlabel('Schaltfrequenz f_sw [kHz]')
    ax1.set_ylabel('Induktivität [mH]')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Subplot 2: Kondensatoren (Kapazitäten)
    # C_f hängt von der Netzfrequenz ab, nicht von der Schaltfrequenz, daher konstant!
    C_f_list = [C_f_calc * 1e6] * len(f_sw_sweep) 
    
    ax2.plot(f_sw_sweep / 1000, C_q_list, label='C_qZSI', color='#d62728', linewidth=2)
    ax2.plot(f_sw_sweep / 1000, C_f_list, label='C_f (LCL-Filter)', color='#9467bd', linewidth=2)
    ax2.set_title('Verkleinerung der Kondensatoren')
    ax2.set_xlabel('Schaltfrequenz f_sw [kHz]')
    ax2.set_ylabel('Kapazität [µF]')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()

    plt.suptitle('Einfluss der Schaltfrequenz auf die passiven Bauteilgrößen', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

ENABLE_SIM = True  # <--- HIER EIN- UND AUSSCHALTEN (True / False)
if ENABLE_SIM:
    run_plecs_simulation(model_name, plecs_params)
# --- 6. WIRKUNGSGRAD AUS CSV ---
csv_pfad_eta = r"C:/MCI_MECH_6/Bachelor/PLECS/Wirkungsgrad.csv"

daten_eta = np.genfromtxt(csv_pfad_eta, delimiter=',', skip_header=1)

# Maske für den eingeschwungenen Zustand (z.B. 0.05s bis 0.1s)
mask_eta = (daten_eta[:, 0] >= 0.05) & (daten_eta[:, 0] <= 0.1)

# Durchschnittswert berechnen
eta_val = np.mean(daten_eta[mask_eta, 1])

if eta_val < 2.0:  # Falls PLECS 0.95 statt 95% ausgibt
    eta_val *= 100

# Einfache Ausgabe in der Konsole
print(f"\nMittlerer Wirkungsgrad: {eta_val:.2f} %")

Enable_debug = True # <--- HIER EIN- UND AUSSCHALTEN (True / False)
if Enable_debug:
    # alle werte ausgeben die wichtig sind für das system 
    I_in = P_n / V_in

    I_phase_neutral_rms = P_n / (math.sqrt(3) * V_pp_rms)
    print(f"I_out       : {I_phase_neutral_rms:.2f} A")
    print(f"I_in       : {I_in:.2f} A")
    print(f"v_ln       : {v_ln:.9f} V")
    print(f"G          : {G:.3f}")
    print(f"M          : {M:.3f}")
    print(f"D          : {D:.3f}")
    print(f"B          : {B:.3f}")
    print(f"V_pn       : {V_pn:.2f} V")
    print(f"V_c1       : {V_c1:.2f} V")
    print(f"V_c2       : {V_c2:.2f} V")
    print(f"T0         : {T0:.9f} s")
    print(f"T0_max     : {T0_max:.9f} s")
    