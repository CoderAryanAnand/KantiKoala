<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue?style=for-the-badge)](README.md)
[![German](https://img.shields.io/badge/Sprache-Deutsch-lightgray?style=for-the-badge)](README.de.md)


# 🐨 KantiKoala

**Die Studienhilfsapp für Schüler:innen der Kanti Baden**

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=for-the-badge&logo=digitalOcean&logoColor=white)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/CoderAryanAnand/KantiKoala/tests.yml?style=for-the-badge&logo=github)



[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-project-structure) • [Contributing](#-contributing)

</div>

---

### 🎓 Maturitätsarbeit

This project was developed as part of a **Maturitätsarbeit** (Matura Thesis) at the **Kantonsschule Baden** (Switzerland).

The goal of the thesis was to investigate how digital tools can improve the study habits of high school students and to implement a practical solution based on those findings. The application combines theoretical research on learning algorithms with modern web development practices.

## 📖 About

KantiKoala is a comprehensive study assistance application designed specifically for students at Kanti Baden. The platform provides tools and resources to help students manage their studies more effectively.

### 🎯 Features

- 📚 **Study Resources** - Curated learning tips
- 📅 **Agenda** - An agenda with a learning time algorithm
- 📊 **Grade management** - A place to store and organize grades
- 📃 **To-Do List** - To-Do list organization
- 👥 **User Management** - Secure authentication
- 🎨 **Modern UI** - Responsive design with TailwindCSS
- 🔒 **Secure** - Industry-standard security practices

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13** (which is recommended, but `3.8` should work as well)
- **Node.js & npm** (for TailwindCSS compilation)
- **PostgreSQL** (for production) or **SQLite** (for development)

### 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CoderAryanAnand/KantiKoala.git
   cd KantiKoala
   ```

2. **Set up Python virtual environment**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies** (for TailwindCSS)
   ```bash
   npm install
   ```

### ⚙️ Configuration

1. **Create a `.env` file** in the root directory:
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   
   # Database Configuration
   DATABASE_URL=sqlite:///dev.db  # For development
   # DATABASE_URL=postgresql://user:password@localhost/dbname  # For production
   
   # Email Configuration (optional)
   RESEND_API_PASSWORD=your-resend-api-key
   
   # Flask Environment
   FLASK_ENV=development
   ```

2. **Initialize the database**
   ```bash
   flask db upgrade
   ```

### 🏃 Running Locally

1. **Development Mode**:
   ```bash
   flask run
   ```

2. **Production Mode** (using Gunicorn):
   ```bash
   gunicorn --bind 0.0.0.0:8080 wsgi:application
   ```

3. **Access the application**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### 🎨 Building TailwindCSS

To compile TailwindCSS styles during development:

```bash
npx tailwindcss -i ./kkoala/static/main.css -o ./kkoala/static/output.css --watch
```

---

## 📂 Project Structure

```
KantiKoala/
├── kkoala/                 # Main application package
│   ├── __init__.py        # Application factory
│   ├── algorithms.py      # Core algorithms
│   ├── config.py          # Configuration settings
│   ├── models.py          # Database models
│   ├── utils.py           # Utility functions
│   ├── routes/            # Route blueprints
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # Jinja2 templates
│   └── tips/              # Study tips content
├── migrations/            # Database migrations
├── report/               # Project documentation
├── requirements.txt      # Python dependencies
├── package.json         # Node.js dependencies
├── tailwind.config.js   # TailwindCSS configuration
├── wsgi.py             # WSGI entry point
└── Procfile            # Heroku deployment config
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Flask 3.1.0, Python 3.13 |
| **Database** | SQLAlchemy 2.0, PostgreSQL / SQLite |
| **Authentication** | Flask-Bcrypt |
| **Frontend** | Jinja2, TailwindCSS 3.4 |
| **Email** | Resend API |
| **Deployment** | Gunicorn |

---

## 🗃️ Database Management

### Create New Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

---

## 📝 Environment Configurations

The application supports multiple configurations:

- **`DevConfig`** - Development environment with debug mode and SQLite
- **`ProdConfig`** - Production environment with PostgreSQL
- **`TestConfig`** - Testing environment with in-memory database

Switch configurations by modifying `wsgi.py`:

```python
config = "kkoala.config.DevConfig"  # or ProdConfig, TestConfig
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👥 Team

- **Maintainer**: [Aryan Anand](https://github.com/CoderAryanAnand)
- **Research**: [Simon Haddon](https://github.com/Komet07)

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🐛 Issues & Support

If you encounter any issues or have questions:

- 📋 [Open an Issue](https://github.com/CoderAryanAnand/KantiKoala/issues)
- 💬 Contact the maintainer

---


<div align="center">

**Made with ❤️ for Kanti Baden students**

⭐ Star this repository if you find it helpful! 

</div>