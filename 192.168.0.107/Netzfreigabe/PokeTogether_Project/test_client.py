import asyncio
import websockets
import socket

async def connect_and_send(uri):
    """Verbindet mit dem Server und sendet eine Testnachricht"""
    try:
        print(f"Verbinde mit {uri}...")
        async with websockets.connect(uri) as websocket:
            print(f"Verbunden mit {uri}")
            
            # Testnachricht senden
            message = "Hallo, Server!"
            print(f"Sende: {message}")
            await websocket.send(message)
            
            # Antwort empfangen
            response = await websocket.recv()
            print(f"Empfangen: {response}")
            
            # Weitere Testnachricht senden
            message = "Wie geht es dir?"
            print(f"Sende: {message}")
            await websocket.send(message)
            
            # Antwort empfangen
            response = await websocket.recv()
            print(f"Empfangen: {response}")
            
            print("Test erfolgreich!")
    except Exception as e:
        print(f"Fehler: {e}")

async def main():
    """Hauptfunktion"""
    # Hostname und IP-Adressen ausgeben
    hostname = socket.gethostname()
    print(f"Client-Hostname: {hostname}")
    
    # Alle IP-Adressen des Hosts ausgeben
    ip_addresses = socket.getaddrinfo(hostname, None)
    print("Client verfügbare IP-Adressen:")
    for ip in ip_addresses:
        if ip[0] == socket.AF_INET:  # Nur IPv4-Adressen
            print(f"  - {ip[4][0]}")
    
    # Server-IP-Adresse abfragen
    server_ip = input("Bitte gib die IP-Adresse des Servers ein: ")
    uri = f"ws://{server_ip}:8765"
    
    # Mit Server verbinden und Testnachricht senden
    await connect_and_send(uri)

if __name__ == "__main__":
    asyncio.run(main())
