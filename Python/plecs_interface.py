import xmlrpc.client

def run_plecs_simulation(model_name, parameters, host="localhost", port=1080):
    """Sendet Parameter an PLECS und startet die Simulation über XML-RPC."""
    try:
        url = f"http://{host}:{port}/RPC2"
        server = xmlrpc.client.ServerProxy(url)
        
        # Verpacken der Parameter für PLECS
        opts = {'ModelVars': parameters}
        
        print(f"Sende Parameter für Modell '{model_name}'...")
        print("Starte Simulation in PLECS... bitte warten...")
        
        # Simulation ausführen
        results = server.plecs.simulate(model_name, opts)
        
        print("Simulation erfolgreich beendet!\n")
        return results
        
    except Exception as e:
        print("\n[FEHLER] Kommunikation mit PLECS fehlgeschlagen.")
        print("Bitte überprüfe, ob:")
        print("1. PLECS im Hintergrund geöffnet ist.")
        print("2. Das XML-RPC Interface in PLECS (Port 1080) aktiv ist.")
        print(f"Details: {e}")
        return None