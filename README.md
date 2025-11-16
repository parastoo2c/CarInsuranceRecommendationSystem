# Multi-Criteria Insurance Recommender System (MCRS)

![Status](https://img.shields.io/badge/Status-Core_Complete-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![Django](https://img.shields.io/badge/Django-5.0-green)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-brightgreen)
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
- **Chrome Extension**: Quick recommendations in your browser
- **AI Extraction**: LLM-powered plan data extraction
- **Configurable Weights**: User-customizable criteria importance
- **Real-time Scoring**: Instant plan ranking and comparison

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
brew services start mongodb-community  # macOS
sudo systemctl start mongod             # Linux

# Load seed data
python3 scripts/load_data.py
```

### Running the Application

**Terminal 1 - Flask API:**
```bash
cd flask_service
source venv/bin/activate
python app.py
# → http://localhost:5000
```

**Terminal 2 - Django Dashboard:**
```bash
cd django_app
source venv/bin/activate
python manage.py runserver
# → http://localhost:8000
```

**Access the dashboard**: Open [http://localhost:8000](http://localhost:8000) in your browser!

### Using Docker (Alternative)

```bash
docker-compose up --build
# Access: http://localhost:8000
```

## 📊 Demo

Try a sample query:
1. Navigate to [http://localhost:8000/search/](http://localhost:8000/search/)
2. Enter:
   - **Vehicle Make**: Toyota
   - **Vehicle Model**: Camry
   - **ZIP Code**: 90210
3. Click "Get Recommendations"
4. View Top 3 plans with transparent scoring!

## 📁 Project Structure

```
insurance-recommender/
├── django_app/              # Django web dashboard
│   ├── dashboard/           # Main Django project
│   ├── recommender/         # Recommender app
│   ├── manage.py
│   └── requirements.txt
├── flask_service/           # Flask microservice for AI & scoring
│   ├── app.py
│   ├── models/              # Scoring algorithms (TOPSIS, etc.)
│   ├── extraction/          # LLM data extraction
│   ├── utils/               # Helper functions
│   └── requirements.txt
├── chrome_extension/        # Chrome Extension (MV3)
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── data/                    # Seed data and datasets
│   ├── seed_insurers.json
│   ├── seed_plans.json
│   └── seed_vehicles.json
├── docker-compose.yml       # Docker orchestration
└── README.md
```

## Tech Stack

- **Backend**: Django 5.x, Flask 3.x, Python 3.11
- **Database**: MongoDB Atlas / Local MongoDB
- **AI/ML**: scikit-learn, XGBoost, SHAP
- **Frontend**: HTML5, CSS3 (Tailwind), Chart.js
- **Deployment**: Docker, GitHub Actions

## Quick Start

### Local Setup (Without Docker)

1. **Install MongoDB** (if not using Atlas):
   ```bash
   brew install mongodb-community  # macOS
   brew services start mongodb-community
   ```

2. **Setup Flask Service**:
   ```bash
   cd flask_service
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

3. **Setup Django App**:
   ```bash
   cd django_app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

### Docker Setup

```bash
docker-compose up --build
```

## Features

- ✅ Multi-criteria recommendation engine (TOPSIS-based)
- ✅ Transparent explainability dashboard
- ✅ AI-powered insurance plan extraction
- ✅ Chrome extension for quick comparisons
- ✅ Configurable weighting system
- ✅ Data lineage tracking

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Complete setup guide with troubleshooting |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Technical architecture and extension guide |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current implementation status and roadmap |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment instructions |
| [Project Proposal](../Parastoo%20-%20Project%20Proposal%20Draft.md) | Original research proposal and methodology |

## 🏗️ Architecture

```
┌──────────────┐
│   Browser    │ ◄─── HTML/CSS/JS
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│    Django    │ ◄─── Templates + Views
│  Dashboard   │
└──────┬───────┘
       │ REST API
       ▼
┌──────────────┐
│    Flask     │ ◄─── TOPSIS Algorithm
│   Service    │
└──────┬───────┘
       │ PyMongo
       ▼
┌──────────────┐
│   MongoDB    │ ◄─── Collections (plans, signals, etc.)
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

## 🧪 Testing

```bash
# Test Flask API
python3 scripts/test_api.py

# Run unit tests (when implemented)
cd flask_service
pytest tests/

# Test specific endpoint
curl http://localhost:5000/health
```

## 📊 Data

The system includes seed data:
- **5 insurers** (State Farm, Geico, Progressive, Allstate, USAA)
- **7 vehicles** (Toyota Camry, Honda Civic, Ford F-150, etc.)
- **50 insurance plans** with realistic pricing
- **50 service quality signals** calibrated to industry benchmarks

Generate new data:
```bash
cd data
python3 generate_seed_data.py
```

## 🎓 Academic Context

This project demonstrates:
- Multi-criteria decision-making (MCDM)
- Recommender systems design
- Explainable AI principles
- Full-stack development
- Microservices architecture
- Data-driven decision support

### References

- J.D. Power (2024). *U.S. Auto Insurance Study*
- ScienceDirect (2024). *TOPSIS Method Survey*
- ACM (2024). *Multi-Criteria Recommender Systems*
- NAIC (2025). *Auto Insurance Database Report*

See [Project Proposal](../Parastoo%20-%20Project%20Proposal%20Draft.md) for complete bibliography.

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 3.x, Django 5.x |
| **Database** | MongoDB 7.x |
| **Frontend** | HTML5, Tailwind CSS, Chart.js |
| **AI/ML** | scikit-learn, NumPy, Pandas |
| **API** | RESTful with Pydantic validation |
| **Deployment** | Docker, Docker Compose |
| **Extension** | Chrome Manifest V3 |

## 🌟 Future Enhancements

### Phase 4 (Pending)
- [ ] Price-only baseline comparator
- [ ] Benchmarking with nDCG and Kendall's Tau
- [ ] Performance optimization with Redis
- [ ] Synthetic user satisfaction simulation

### Phase 5 (Pending)
- [ ] Governance dashboard
- [ ] Data lineage tracking
- [ ] Bias detection and reporting
- [ ] Final presentation materials

### Beyond MVP
- [ ] User accounts and saved searches
- [ ] Real-time data integration with insurer APIs
- [ ] Machine learning ranking models (XGBoost)
- [ ] Mobile app (React Native)
- [ ] Multi-state support

## 🤝 Contributing

This is an academic project, but suggestions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 Project Status

**✅ Completed**: Phases 1-3 (Core functionality, explainability, Chrome extension)  
**⏳ Pending**: Phases 4-5 (Benchmarking, governance documentation)

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed progress.

## 🐛 Known Issues

- Requires API keys for full LLM extraction (fallback available)
- Limited to California ZIP codes (by design)
- Synthetic data only (no real insurer API integration)

## 📄 License

MIT License - Academic/Research Project

## 👤 Author

**Parastoo Toosi**  
Computer Science Department  
California State University, Fullerton (CSUF)

**Advisor**: Dr. Rong Jin

## 🙏 Acknowledgments

- J.D. Power for auto insurance research
- NAIC for regulatory data insights
- CSUF Computer Science Department
- Open-source community

## 📧 Contact

For questions or collaboration:
- See documentation in this repository
- Check [GETTING_STARTED.md](GETTING_STARTED.md) for setup help
- Review [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for technical details

---

**Built with ❤️ for better insurance decisions**

