# Arbeitsabfolge mit lokalen Berichten und GitHub-Integration

Diese Arbeitsabfolge beschreibt den strukturierten Prozess zur Entwicklung von Features und Lösung von Problemen im PokeTogether-Projekt unter Verwendung von lokalen Berichten mit GitHub-Integration.

## Schritte

1. **GitHub Issues und TODO-Liste prüfen und aktualisieren**
   - Neue GitHub Issues prüfen und in die TODO-Liste einarbeiten
   - Bestehende TODO-Liste mit allen geplanten Features prüfen
   - Abgeschlossene Features mit [x] markieren
   - Zusätzliche Features oder Verbesserungen hinzufügen, falls nötig
   - Sicherstellen, dass alle Einträge und Untereinträge Checkboxen haben ([ ] oder [x])
   - Aktualisierte Liste im Agent-Memory merken

2. **Nächstes offenes Feature auswählen**
   - Feature bestimmen, das als Nächstes umgesetzt werden soll

3. **GitHub Issue-Inhalt vorbereiten**
   - Inhalt für ein neues Issue zum Feature erstellen
   - Detaillierte Beschreibung des Features verfassen
   - Anforderungen und Akzeptanzkriterien definieren
   - Vorschläge für relevante Labels (z.B. "enhancement", "multiplayer", "ui")
   - Prioritätsvorschlag machen
   - Inhalt in einer Datei im `github/` Verzeichnis speichern

4. **Feature-Integration analysieren**
   - Technische Integration des Features planen
   - Code-Review durchführen
   - Logs und bisherige Testberichte prüfen
   - Analyse in einem Problembericht dokumentieren
   - Problembericht im `reports/` Verzeichnis speichern

5. **Feature implementieren**
   - Feature umsetzen
   - Code-Qualität und Konsistenz sicherstellen
   - Ausreichend Logging-Stellen hinzufügen
   - Regelmäßige Commits mit aussagekräftigen Commit-Nachrichten

6. **Feature testen**
   - Tests durchführen
   - Logs und Testberichte analysieren
   - Screenshots oder Dokumentationen erstellen
   - Testergebnisse in einem Zwischenbericht dokumentieren
   - Zwischenbericht im `reports/` Verzeichnis speichern

7. **Problem analysieren (falls aufgetreten)**
   - Gründliche Analyse des Problems durchführen
   - Logs und Testberichte überprüfen
   - Relevante Codestellen identifizieren
   - Analyse in einem Problembericht dokumentieren
   - Problembericht im `reports/` Verzeichnis speichern
   - Vorbereiteten Kommentar für GitHub im `github/` Verzeichnis speichern

8. **Lösungsansatz entwickeln**
   - Lösungsansätze für identifizierte Probleme vorschlagen
   - Vor- und Nachteile verschiedener Ansätze abwägen
   - Lösungsansatz im Problembericht dokumentieren
   - Vorbereiteten Kommentar für GitHub im `github/` Verzeichnis aktualisieren

9. **Implementation durchführen**
   - Änderungen gemäß dem Lösungsansatz implementieren
   - Code-Qualität und Konsistenz sicherstellen
   - Ausreichende Logging-Stellen hinzufügen

10. **Test durchführen**
    - Implementierung testen
    - Logs und Testberichte analysieren
    - Screenshots erstellen, falls relevant
    - Testergebnisse in einem Zwischenbericht dokumentieren
    - Zwischenbericht im `reports/` Verzeichnis speichern
    - Vorbereiteten Kommentar für GitHub im `github/` Verzeichnis aktualisieren

11. **Änderungen auf Git pushen**
    - Relevante Dateien zum Commit hinzufügen
    - Aussagekräftige Commit-Nachricht erstellen
    - Änderungen auf den entsprechenden Branch pushen
    - Commit-Informationen im Zwischenbericht dokumentieren

12. **Verbleibende Probleme analysieren**
    - Gründliche Analyse der verbleibenden Probleme
    - Logs und Testberichte überprüfen
    - Relevante Codestellen identifizieren
    - Analyse in einem aktualisierten Problembericht dokumentieren
    - Problembericht im `reports/` Verzeichnis aktualisieren
    - Vorbereiteten Kommentar für GitHub im `github/` Verzeichnis aktualisieren

13. **Diesen Zyklus fortsetzen, bis alle Probleme gelöst sind**
    - Schritte 8-12 wiederholen, bis alle Probleme gelöst sind

14. **Zusätzliche Logging-Stellen implementieren**
    - Tiefgreifende Verifizierung, dass alles wie erwartet funktioniert
    - Ausführliche Logging-Stellen hinzufügen
    - Vergleich mit erwartetem Verhalten

15. **Refactoring durchführen**
    - Umfangreiches Refactoring nach jedem Feature planen
    - Code auf Redundanzen und übermäßige Dateigrößen prüfen
    - Große Klassen und Methoden in kleinere, fokussierte Einheiten aufteilen
    - Gemeinsame Funktionalitäten in Hilfsklassen oder -methoden extrahieren
    - Konsistente Namenskonventionen und Codestruktur sicherstellen
    - Refactoring-Plan im `reports/` Verzeichnis dokumentieren

16. **Umfassende Tests nach Refactoring durchführen**
    - Alle betroffenen Funktionalitäten gründlich testen
    - Regressionen identifizieren und beheben
    - Sicherstellen, dass das refactorierte Spiel ohne Fehler und Probleme funktioniert
    - Testergebnisse dokumentieren

17. **Abschlussbericht erstellen**
    - Zusammenfassung aller durchgeführten Änderungen dokumentieren
    - Beschreibung der Testergebnisse
    - Dokumentation des Refactorings und seiner Vorteile
    - Empfehlungen für zukünftige Verbesserungen
    - Abschlussbericht im `reports/` Verzeichnis speichern
    - Vorbereiteten Abschlusskommentar für GitHub im `github/` Verzeichnis speichern

18. **Feature in der TODO-Liste abhaken**
    - Umgesetztes Feature als erledigt markieren ([x])

19. **TODO-Liste anpassen und merken**
    - Prüfen, ob neue Features oder Verbesserungen eingetragen werden sollen
    - Liste aktualisieren und im Agent-Memory merken

20. **Nächstes Feature auswählen und Prozess wiederholen**
    - Nächstes offenes Feature auswählen
    - Gesamten Ablauf ab Schritt 3 wiederholen

## Vorteile der kombinierten Methode

1. **Autonomes Arbeiten**: Lokale Berichte ermöglichen autonomes Arbeiten ohne ständige Bestätigung
2. **Strukturierte Dokumentation**: Klare Trennung zwischen internen Berichten und GitHub-Inhalten
3. **Nachverfolgbarkeit**: Vollständige Historie der Probleme, Lösungen und Entscheidungen
4. **GitHub-Integration**: Vorbereitung von Inhalten für GitHub ohne direkte API-Aufrufe
5. **Flexibilität**: Der Benutzer kann GitHub-Inhalte nach Bedarf posten

## Hinweise

- Berichte im `reports/` Verzeichnis speichern mit aussagekräftigen Namen (z.B. `Feature_Name_Problembericht_Datum.md`)
- GitHub-Inhalte im `github/` Verzeichnis speichern mit klaren Referenzen zum Issue (z.B. `issue_42_comment.md`)
- Bei Berichten klare Überschriften verwenden (z.B. "Analyse", "Lösungsansatz", "Testergebnisse")
- Relevante Code-Snippets in Berichten mit Markdown-Formatierung einbinden
- Screenshots in Berichten referenzieren und im `screenshots/` Verzeichnis speichern
- Bei Commits immer aussagekräftige Nachrichten verwenden
- Regelmäßig die TODO-Liste aktualisieren, um den Fortschritt zu dokumentieren
