import requests
import json
from collections import defaultdict
import time
import sys

def fetch_events():
    """Holt Events von der Quelle"""
    try:
        response = requests.get('http://assessment:8080/v1/dataset', timeout=30)
        response.raise_for_status()  # Wirft Exception bei HTTP-Fehlern
        return response.json()['events']
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Events: {e}")
        sys.exit(1)

def calculate_consumption(events):
    """Berechnet Nutzungszeit pro Kunde"""
    # Sammle Start- und Stop-Events pro Workload
    workload_events = defaultdict(list)
    
    for event in events:
        key = (event['customerId'], event['workloadId'])
        workload_events[key].append(event)
    
    # Berechne Nutzungszeit pro Kunde
    customer_times = defaultdict(int)
    
    for (customer_id, workload_id), events in workload_events.items():
        start_time = None
        stop_time = None
        
        for event in events:
            if event['eventType'] == 'start':
                start_time = event['timestamp']
            elif event['eventType'] == 'stop':
                stop_time = event['timestamp']
        
        if start_time and stop_time:
            duration = stop_time - start_time
            customer_times[customer_id] += duration
    
    # Formatierung für das Ergebnis
    result = []
    for customer_id, consumption in customer_times.items():
        result.append({
            'customerId': customer_id,
            'consumption': consumption
        })
    
    return result

def send_results(results):
    """Sendet Ergebnisse an das Referenzsystem"""
    payload = {'result': results}
    response = requests.post(
        'http://assessment:8080/v1/result', 
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    return response.status_code

def main():
    print("Starte Berechnung...")
    
    # 1. Events abrufen
    events = fetch_events()
    print(f"Empfange {len(events)} Events")
    
    # 2. Nutzungszeit berechnen
    results = calculate_consumption(events)
    print(f"Berechne Nutzungszeit für {len(results)} Kunden")
    
    # 3. Ergebnisse senden
    status_code = send_results(results)
    print(f"Ergebnisse gesendet - Status: {status_code}")

# HIER IST DIE KORRIGIERTE ZEILE:
if __name__ == "__main__":
    main()