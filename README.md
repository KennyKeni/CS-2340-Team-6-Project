# CS-2340 Team 6 Project

A Django web application for CS-2340 class project, built with modern Python tooling using UV package manager.

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/) - Fast Python package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KennyKeni/CS-2340-Team-6-Project
   cd CS-2340-Team-6-Project
   ```

2. **Install UV (if not already installed)**
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**
   ```bash
   # UV automatically creates and manages a virtual environment
   # To activate it manually:
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

## 🛠️ Development

### Running the Development Server

1. **Apply database migrations**
   ```bash
   uv run python manage.py migrate
   ```

2. **Create a superuser (optional)**
   ```bash
   uv run python manage.py createsuperuser
   ```

3. **Start the development server**
   ```bash
   uv run python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`

### Common Commands

```bash
# Run Django management commands
uv run python manage.py <command>

# Install new dependencies
uv add <package-name>

# Install development dependencies
uv add --dev <package-name>

# Remove dependencies
uv remove <package-name>

# Update all dependencies
uv lock --upgrade

# Run tests
uv run python manage.py test

# Collect static files
uv run python manage.py collectstatic
```

## 📁 Project Structure

```
CS-2340-Team-6-Project/
├── job_app/                # Main Django project directory
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── manage.py              # Django management script
├── db.sqlite3            # SQLite database (created after migrations)
├── pyproject.toml        # Project configuration and dependencies
├── uv.lock              # Lock file for reproducible builds
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

### Database

The project is configured to use SQLite by default, which is suitable for development. This will not be the final database of choice.

## 📦 Dependencies

- **Django 5.2.6+**: Web framework
- **Pillow 11.3.0+**: Python Imaging Library for image processing

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Python Package Index](https://pypi.org/)

## 👥 Team

CS-2340 Team 6

- Deven (Scrum Master + Frontend Dev )
- Jahir (Product Owner + Backend Dev)
- Kenny (Backend Dev)
- Sayan (Full Stack Dev)
- Shashwat (Frontend Dev)
