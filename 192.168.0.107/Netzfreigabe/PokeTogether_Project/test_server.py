import asyncio
import websockets
import socket

async def echo(websocket):
    """Echo server - sendet alle empfangenen Nachrichten zurück"""
    print(f"Client verbunden: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Empfangen: {message}")
            await websocket.send(f"Echo: {message}")
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        print(f"Client getrennt: {websocket.remote_address}")

async def main():
    """Startet den WebSocket-Server"""
    # Hostname und IP-Adressen ausgeben
    hostname = socket.gethostname()
    print(f"Hostname: {hostname}")
    
    # Alle IP-Adressen des Hosts ausgeben
    ip_addresses = socket.getaddrinfo(hostname, None)
    print("Verfügbare IP-Adressen:")
    for ip in ip_addresses:
        if ip[0] == socket.AF_INET:  # Nur IPv4-Adressen
            print(f"  - {ip[4][0]}")
    
    # Server starten
    host = "0.0.0.0"  # Auf allen Interfaces lauschen
    port = 8765
    print(f"Server wird gestartet auf {host}:{port}...")
    
    async with websockets.serve(echo, host, port):
        print(f"Server läuft auf {host}:{port}")
        await asyncio.Future()  # Läuft für immer

if __name__ == "__main__":
    asyncio.run(main())
