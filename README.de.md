<div align="center">

<!-- Language Switch -->
[![English](https://img.shields.io/badge/Language-English-lightgray?style=for-the-badge)](README.md)
[![German](https://img.shields.io/badge/Sprache-Deutsch-blue?style=for-the-badge)](README.de.md)

# 🐨 KantiKoala

**Die Lernhilfe-App für Schüler:innen der Kanti Baden**

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=for-the-badge&logo=digitalOcean&logoColor=white)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/CoderAryanAnand/KantiKoala/tests.yml?style=for-the-badge&logo=github)


</div>

---

### 🎓 Maturitätsarbeit

Dieses Projekt wurde im Rahmen einer **Maturitätsarbeit** an der **Kantonsschule Baden** (Schweiz) entwickelt.

Ziel der Arbeit war es, zu untersuchen, wie digitale Werkzeuge das Lernverhalten von Gymnasiast:innen verbessern können, und basierend auf diesen Erkenntnissen eine praktische Lösung zu implementieren. Die Anwendung verbindet theoretische Forschung zu Lernalgorithmen mit moderner Webentwicklung.

## 📖 Über das Projekt

KantiKoala ist eine umfassende Lernhilfe-Applikation, die speziell für Schüler:innen der Kanti Baden entwickelt wurde. Die Plattform bietet Werkzeuge und Ressourcen, um das Lernen effektiver zu gestalten und den Schulalltag besser zu organisieren.

### 🎯 Funktionen

- 📚 **Lernressourcen** – Ausgewählte Lerntipps
- 📅 **Agenda** – Eine Agenda mit einem Algorithmus für die Lernzeit
- 📊 **Notenverwaltung** – Ein Ort zum Speichern und Organisieren von Noten
- 📃 **To-Do-Liste** – Organisation der To-Do-Liste
- 👥 **Benutzerverwaltung** – Sichere Authentifizierung
- 🎨 **Moderne Benutzeroberfläche** – Responsives Design mit TailwindCSS
- 🔒 **Sicher** – Sicherheitsstandards nach Branchennorm

---

## 🚀 Schnell-Start

### Voraussetzungen

- **Python 3.13** (empfohlen, aber `3.8` sollte ebenfalls funktionieren)
- **Node.js & npm** (für die TailwindCSS-Kompilierung)
- **PostgreSQL** (für die Produktion) oder **SQLite** (für die Entwicklung)

### 📥 Installation

1. **Repository klonen**

   ```bash
   git clone https://github.com/CoderAryanAnand/KantiKoala.git
   cd KantiKoala
   ```

2. **Python-virtuelle Umgebung einrichten**

   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Python-Abhängigkeiten installieren**

   ```bash
   pip install -r requirements.txt
   ```

4. **Node.js-Abhängigkeiten installieren** (für TailwindCSS)

   ```bash
   npm install
   ```

### ⚙️ Konfiguration

1. **Eine `.env`-Datei erstellen** im Projektverzeichnis:

   ```env
   # Flask-Konfiguration
   SECRET_KEY=your-secret-key-here

   # Datenbank-Konfiguration
   DATABASE_URL=sqlite:///dev.db  # Für Entwicklung
   # DATABASE_URL=postgresql://user:password@localhost/dbname  # Für Produktion

   # E-Mail-Konfiguration (optional)
   RESEND_API_PASSWORD=your-resend-api-key

   # Flask-Umgebung
   FLASK_ENV=development
   ```

2. **Datenbank initialisieren**

   ```bash
   flask db upgrade
   ```


### 🏃 Lokal ausführen

1.  **Entwicklungsmodus**:

    ```bash
    flask run
    ```

2.  **Produktionsmodus** (mit Gunicorn):

    ```bash
    gunicorn --bind 0.0.0.0:8080 wsgi:application
    ```

3.  **Auf die Anwendung zugreifen**

    Öffnen Sie Ihren Browser und navigieren Sie zu:

    ```
    http://localhost:5000
    ```

### 🎨 TailwindCSS bauen

Um TailwindCSS-Styles während der Entwicklung zu kompilieren:

```bash
npx tailwindcss -i ./kkoala/static/main.css -o ./kkoala/static/output.css --watch
```

-----

## 📂 Projektstruktur

```
KantiKoala/
├── kkoala/                # Hauptanwendungspaket
│   ├── __init__.py        # Anwendungs-Factory
│   ├── algorithms.py      # Kernalgorithmen
│   ├── config.py          # Konfigurationseinstellungen
│   ├── models.py          # Datenbankmodelle
│   ├── utils.py           # Hilfsfunktionen
│   ├── routes/            # Route-Blueprints
│   ├── static/            # Statische Dateien (CSS, JS, Bilder)
│   ├── templates/         # Jinja2 Templates
│   └── tips/              # Inhalt der Lerntipps
├── migrations/            # Datenbank-Migrationen
├── report/                # Projektdokumentation
├── requirements.txt       # Python-Abhängigkeiten
├── package.json           # Node.js-Abhängigkeiten
├── tailwind.config.js     # TailwindCSS-Konfiguration
├── wsgi.py                # WSGI-Einstiegspunkt
└── Procfile               # Heroku-Deployment-Konfig
```

-----

## 🛠️ Technologie-Stack

| Kategorie | Technologien |
|----------|-------------|
| **Backend** | Flask 3.1.0, Python 3.13 |
| **Datenbank** | SQLAlchemy 2.0, PostgreSQL / SQLite |
| **Authentifizierung** | Flask-Bcrypt |
| **Frontend** | Jinja2, TailwindCSS 3.4 |
| **E-Mail** | Resend API |
| **Deployment** | Gunicorn |

-----

## 🗃️ Datenbankverwaltung

### Neue Migration erstellen

```bash
flask db migrate -m "Beschreibung der Änderungen"
```

### Migrationen anwenden

```bash
flask db upgrade
```

### Migration rückgängig machen

```bash
flask db downgrade
```

-----

## 📝 Umgebungskonfigurationen

Die Anwendung unterstützt mehrere Konfigurationen:

  - **`DevConfig`** - Entwicklungsumgebung mit Debug-Modus und SQLite
  - **`ProdConfig`** - Produktionsumgebung mit PostgreSQL
  - **`TestConfig`** - Testumgebung mit In-Memory-Datenbank

Wechseln Sie die Konfigurationen durch Ändern von `wsgi.py`:

```python
config = "kkoala.config.DevConfig"  # oder ProdConfig, TestConfig
```

-----

## 🤝 Mitwirken

Beiträge sind willkommen! Zögern Sie nicht, einen Pull Request einzureichen.

1.  Forken Sie das Repository
2.  Erstellen Sie Ihren Feature-Branch (`git checkout -b feature/TollesFeature`)
3.  Committen Sie Ihre Änderungen (`git commit -m 'Füge ein TollesFeature hinzu'`)
4.  Pushen Sie auf den Branch (`git push origin feature/TollesFeature`)
5.  Öffnen Sie einen Pull Request

-----

## 👥 Team

  - **Maintainer**: [Aryan Anand](https://github.com/CoderAryanAnand)
  - **Recherche**: [Simon Haddon](https://github.com/Komet07)

-----

## 📄 Lizenz

Dieses Projekt ist unter der Apache License 2.0 lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.

-----

## 🐛 Probleme & Support

Wenn Sie auf Probleme stoßen oder Fragen haben:

  - 📋 [Öffnen Sie ein Issue](https://github.com/CoderAryanAnand/KantiKoala/issues)
  - 💬 Kontaktieren Sie den Maintainer

-----

<div align="center">

**Mit ❤️ für Schüler:innen der Kanti Baden gemacht**

⭐ Geben Sie diesem Repository einen Stern, wenn Sie es hilfreich finden!

</div>

