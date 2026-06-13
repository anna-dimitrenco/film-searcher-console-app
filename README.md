# 🎬 Film Searcher — Konsolenanwendung zur Filmsuche

## Stell dir vor, du suchst schnell einen Film nach Genre oder Titel — direkt im Terminal, ohne Browser. Genau das macht diese App.

#### Film Searcher ist eine interaktive Konsolenanwendung, die die Sakila-Datenbank (MySQL) durchsucht und dabei jeden Suchverlauf automatisch in MongoDB speichert — damit du immer weißt, was gerade beliebt ist.

### 🎯 Projektziel

#### Eine Konsolen-Suchmaschine für Filme erstellen, die Folgendes ermöglicht:

- Filme nach Stichwort suchen
- Filme nach Genre und Erscheinungsjahr suchen
- Suchverlauf in MongoDB speichern
- Statistik der beliebtesten Suchanfragen anzeigen

###  🛠️ Technologien

- Python 3
- MySQL — Sakila-Datenbank (Filme, Genres)
- MongoDB — Protokollierung der Suchanfragen
- pymysql — Verbindung zu MySQL
- pymongo — Verbindung zu MongoDB
- rich — Formatierte Konsolenausgabe


### 📁 Projektstruktur

#### film-searcher-console-app/

|── main.py -> Einstiegspunkt, Hauptschleife

|── config.py -> Datenbankverbindungseinstellungen

|── library.py ->  Hauptlogik und Menü

|── mysql_connector.py -> MySQL-Verbindung, SQL-Abfragen

|── mongo_connector.py -> MongoDB-Verbindung

|── formatter.py -> Formatierung der Konsolenausgabe

|── secret.json.example ->  Beispieldatei für Einstellungen

### 🚀 Installation und Start
Voraussetzungen: Python 3, MySQL (Sakila), MongoDB müssen installiert sein.

#### 1.Abhängigkeiten installieren:
pip install pymysql pymongo rich

#### 2.Verbindung konfigurieren:
Die Datei secret.json öffnen und die eigenen Zugangsdaten für MySQL und MongoDB eintragen.

#### 3. Anwendung starten:
python main.py

#### 4. Screenshots
<img width="1770" height="972" alt="Screen_1" src="https://github.com/user-attachments/assets/daf7fa26-234d-4528-ba32-2fcd0a48fe5f" />

<img width="1770" height="972" alt="Screen_2" src="https://github.com/user-attachments/assets/cd59ce11-aae6-4b9e-850e-f834dc1579d4" />

<img width="1770" height="972" alt="Screen_3" src="https://github.com/user-attachments/assets/59fcbf0f-beff-4f4a-b4b0-d4c32083aed1" />



