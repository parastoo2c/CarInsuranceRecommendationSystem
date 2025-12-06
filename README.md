# Multi-Criteria Insurance Recommender System (MCRS)

![Status](https://img.shields.io/badge/Status-Core_Complete-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![Django](https://img.shields.io/badge/Django-5.0-green)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0+-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

An **AI-driven decision aid** that ranks insurance plans by **long-term value**, integrating signals of **cost, coverage quality, and service performance** using the TOPSIS multi-criteria decision-making algorithm.

> **Academic Project** | California State University, Fullerton (CSUF)
> **Prepared by**: Parastoo Toosi
> **Advisor**: Dr. Rong Jin, Department of Computer Science

## 🎯 Project Overview

Most insurance comparison platforms emphasize **lowest premium pricing** as the dominant ranking criterion. This inadvertently fosters **adverse selection** where users select plans that minimize short-term cost but experience poor service quality later.

This system ranks insurance plans using **multi-criteria optimization** across four key dimensions:

- 💰 **Cost Efficiency** - Normalized premium affordability
- 🛡️ **Coverage Adequacy** - IDV and add-on evaluation
- ⚡ **Service Quality** - Claims turnaround, approval rates, satisfaction
- ⭐ **Reliability** - Customer retention and complaint ratios

## ✨ Key Features

- **TOPSIS Algorithm**: Transparent multi-criteria decision-making
- **Explainable AI**: Visual score breakdowns with Chart.js
- **Interactive Dashboard**: Modern web interface built with Django
- **REST API**: Flask microservice for recommendations
- **California-Specific Data**: Real NHTSA vehicle data + CA DOI insurance rates
- **Configurable Weights**: User-customizable criteria importance
- **Real-time Scoring**: Instant plan ranking and comparison
- **Dynamic Data Sources**: Fetch fresh data from external APIs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- Git

### Installation (3 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd insurance-recommender

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start MongoDB (if local)
brew services start mongodb-community # macOS
sudo systemctl start mongod # Linux

# Load seed data
cd flask_service
source myenv/bin/activate
cd ../scripts
python3 load_data.py
```

### Running the Application

**Terminal 1 - Flask API:**
```bash
cd flask_service
source myenv/bin/activate
python app.py
# → http://localhost:5000
```

**Terminal 2 - Django Dashboard:**
```bash
cd django_app
source myenv/bin/activate
python manage.py runserver
# → http://localhost:8000
```

**Access the dashboard**: Open [http://localhost:8000](http://localhost:8000) in your browser!

## 📊 Demo

Try a sample query:
1. Navigate to [http://localhost:8000/search/](http://localhost:8000/search/)
2. Enter:
- **Vehicle Make**: Toyota
- **Vehicle Model**: Camry
- **ZIP Code**: 90210 (Beverly Hills, CA)
- **Year**: 2023
3. Click "Get Recommendations"
4. View Top 3 plans with transparent scoring!

## 📁 Project Structure

```
insurance-recommender/
├── django_app/ # Django web dashboard
│ ├── dashboard/ # Main Django project
│ ├── recommender/ # Recommender app
│ ├── templates/ # HTML templates
│ └── requirements.txt
├── flask_service/ # Flask microservice for AI & scoring
│ ├── app.py # Main API
│ ├── models/ # Scoring algorithms (TOPSIS)
│ ├── extraction/ # LLM data extraction (optional)
│ ├── database.py # MongoDB connection
│ └── requirements.txt
├── data/ # Data generation scripts
│ ├── fetch_external_data.py # Fetch from NHTSA API
│ ├── generate_seed_data.py # Generate plans/signals
│ ├── seed_config.json # CA configuration
│ ├── seed_insurers.json # CA insurers
│ ├── seed_vehicles.json # Vehicle data
│ ├── seed_plans.json # Insurance plans
│ └── seed_signals.json # Quality signals
├── scripts/ # Setup and utility scripts
│ ├── setup.sh # Automated setup
│ ├── load_data.py # Load data to MongoDB
│ ├── generate_env.py # Generate .env file
│ ├── test_california_data.py # Data tests
│ └── test_api.py # API tests
└── README.md
```

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+, Flask 3.x, Django 5.x |
| **Database** | MongoDB 5.0+ |
| **Frontend** | HTML5, CSS3, Chart.js |
| **AI/ML** | scikit-learn, NumPy, Pandas |
| **API** | RESTful with Pydantic validation |
| **Data Sources** | NHTSA API, CA DOI published data |

## 🏗️ Architecture

```
┌──────────────┐
│ Browser │ ◄─── HTML/CSS/JS
└──────┬───────┘
│ HTTP
▼
┌──────────────┐
│ Django │ ◄─── Templates + Views
│ Dashboard │
└──────┬───────┘
│ REST API
▼
┌──────────────┐
│ Flask │ ◄─── TOPSIS Algorithm
│ Service │
└──────┬───────┘
│ PyMongo
▼
┌──────────────┐
│ MongoDB │ ◄─── Collections (insurers, plans, vehicles, signals)
└──────────────┘
```

## 🔬 Methodology

### TOPSIS Algorithm

The system uses **Technique for Order of Preference by Similarity to Ideal Solution**:

1. **Normalize** criteria across different scales
2. **Apply weights** based on user preferences
3. **Calculate distances** to ideal and anti-ideal solutions
4. **Rank alternatives** by relative closeness

### Scoring Formula

For each plan:

```
Score = D⁻ / (D⁺ + D⁻)

where:
D⁺ = distance to ideal solution
D⁻ = distance to anti-ideal solution
```

### Default Weights

- Cost (λ₁): 30%
- Coverage (λ₂): 25%
- Service (λ₃): 25%
- Reliability (λ₄): 20%

*Users can customize these weights in the search interface.*

## 📊 Data

### California-Specific Data

The system uses California-specific insurance data:
- **20 insurers** - Top California insurers by market share
- **150+ vehicles** - Real data from NHTSA API
- **120+ insurance plans** - California-adjusted rates (24% above national average)
- **300+ service quality signals** - Based on CA DOI complaint ratios and J.D. Power ratings

### Data Sources

- **✅ Live from Internet**: NHTSA vehicle data (fetched at setup)
- **📄 Published Data**: CA DOI premium averages, insurer market share, complaint ratios
- **📚 Research-Based**: J.D. Power California satisfaction ratings

Generate fresh data:
```bash
cd data
python3 fetch_external_data.py # Fetch from NHTSA API
python3 generate_seed_data.py # Generate plans/signals
```

## 🧪 Testing

```bash
# Test California data integrity
python3 scripts/test_california_data.py

# Test Flask API
cd flask_service
source myenv/bin/activate
cd ../scripts
python3 test_api.py

# Test Django app
cd django_app
source myenv/bin/activate
python3 manage.py test
```

## 📖 Documentation

### Getting Started
| Document | Description |
|----------|-------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | 🚀 Complete setup guide - Start here! |
| [SETUP_WORKFLOW.md](SETUP_WORKFLOW.md) | Detailed workflow with visual flowcharts |

### Technical Details
| Document | Description |
|----------|-------------|
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | TOPSIS algorithm, API docs, extending the system |
| [data/README.md](data/README.md) | Data generation, sources, and California features |
| [scripts/README.md](scripts/README.md) | Scripts documentation and troubleshooting |

## 🎓 Academic Context

This project demonstrates:
- Multi-criteria decision-making (MCDM)
- Recommender systems design
- Explainable AI principles
- Full-stack development
- Microservices architecture
- Data-driven decision support

## 🌟 Future Enhancements

### Planned Features
- [ ] Price-only baseline comparator
- [ ] Benchmarking with nDCG and Kendall's Tau
- [ ] Performance optimization with Redis caching
- [ ] User accounts and saved searches
- [ ] Real-time data integration with insurer APIs
- [ ] Machine learning ranking models (XGBoost)
- [ ] Multi-state support beyond California

## 📝 Project Status

**✅ Completed**: Core functionality, California data integration, TOPSIS algorithm
**✅ Completed**: Testing and documentation refinement

## 🐛 Known Issues

- Requires API keys for full LLM extraction (optional feature, fallback available)
- Limited to California ZIP codes (by design for this version)
- Uses California DOI published data, not live quote APIs (not publicly available)

## 📄 License

MIT License - Academic/Research Project

## 👤 Author

**Parastoo Toosi**
Computer Science Department
California State University, Fullerton (CSUF)

**Advisor**: Dr. Rong Jin

## 🙏 Acknowledgments

- California Department of Insurance for published data
- National Highway Traffic Safety Administration (NHTSA) for vehicle API access
- J.D. Power for auto insurance research
- CSUF Computer Science Department
- Open-source community

## 📧 Contact

For questions or collaboration:
- Review [GETTING_STARTED.md](GETTING_STARTED.md) for setup help
- Check [SETUP_WORKFLOW.md](SETUP_WORKFLOW.md) for workflow details
- See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for technical details

---

**Built with ❤️ for better insurance decisions**