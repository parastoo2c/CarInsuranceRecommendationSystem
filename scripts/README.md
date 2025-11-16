# Scripts Directory

Utility scripts for setup, data loading, and testing.

## Setup Scripts

### `setup.sh`
Automated setup script that:
- Creates virtual environments for Flask and Django
- Installs all dependencies
- Generates seed data
- Creates `.env` configuration file

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

### `load_data.py`
Loads seed data into MongoDB database.

**Usage:**
```bash
python3 load_data.py
```

**Prerequisites:**
- MongoDB must be running
- Seed data files must exist in `data/` directory

### `test_api.py`
Tests Flask API endpoints.

**Usage:**
```bash
python3 test_api.py
```

**Tests:**
- `/health` - Health check
- `/api/stats` - Database statistics
- `/api/recommend` - Recommendation endpoint

## Quick Start Sequence

```bash
# 1. Run setup
./setup.sh

# 2. Start MongoDB (if local)
brew services start mongodb-community  # macOS

# 3. Load data
python3 load_data.py

# 4. Start Flask service (Terminal 1)
cd ../flask_service
source venv/bin/activate
python app.py

# 5. Start Django app (Terminal 2)
cd ../django_app
source venv/bin/activate
python manage.py migrate
python manage.py runserver

# 6. Test APIs (Terminal 3)
python3 test_api.py

# 7. Open browser
open http://localhost:8000
```

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
brew services list | grep mongodb    # macOS
sudo systemctl status mongod         # Linux

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod           # Linux
```

### Port Already in Use
```bash
# Find and kill process using port
lsof -ti:5000 | xargs kill -9  # Flask
lsof -ti:8000 | xargs kill -9  # Django
```

### Missing Dependencies
```bash
# Reinstall Flask dependencies
cd flask_service
source venv/bin/activate
pip install -r requirements.txt

# Reinstall Django dependencies
cd django_app
source venv/bin/activate
pip install -r requirements.txt
```

### Import Errors
Make sure you're in the correct directory and virtual environment is activated.

