PokeTogether - Installationsanleitung
====================================

Um das Spiel auf einem neuen Computer zu starten, folge bitte diesen Schritten:

1. Installiere Python 3.13 von https://www.python.org/downloads/
   - Stelle sicher, dass du "Add Python to PATH" während der Installation aktivierst

2. Doppelklicke auf die Datei "setup_and_run.bat"
   - Diese Datei installiert alle notwendigen Pakete und startet das Spiel

Alternativ kannst du auch die kompilierte Version verwenden:
- Doppelklicke auf "PokeTogether_debug.exe"
- Falls das Spiel nicht startet, fehlen möglicherweise einige Komponenten:
  - Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - DirectX Runtime: https://www.microsoft.com/en-us/download/details.aspx?id=35

Multiplayer-Modus:
-----------------
1. Auf dem Host-Computer:
   - Starte das Spiel
   - Wähle "Host Game" im Hauptmenü
   - Notiere dir die angezeigte IP-Adresse

2. Auf dem Client-Computer:
   - Starte das Spiel
   - Wähle "Join Game" im Hauptmenü
   - Gib die IP-Adresse des Hosts ein
   - Drücke Enter, um die Verbindung herzustellen

Bei Problemen:
-------------
- Stelle sicher, dass beide Computer im selben Netzwerk sind
- Überprüfe die Firewall-Einstellungen (Port 8765 muss freigegeben sein)
- Versuche, die IP-Adresse des Hosts zu pingen, um die Verbindung zu testen
