# NutriSense 🍱
### An Agentic AI-Based System for Automated Food Analysis, Nutritional Compliance Checking, and Meal Attendance Tracking

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

---

## 📌 Overview

NutriSense is an intelligent, camera-based nutritional monitoring system designed specifically for **Karnataka government school canteens** under the **Mid-Day Meal (MDM) Scheme**. It automates food detection, nutrition analysis, dietary compliance checking, and meal attendance tracking using computer vision, deep learning, and agentic AI.

The system addresses a critical gap in institutional food service: manual nutritional assessment is slow, inconsistent, and cannot scale to hundreds of meals served daily. NutriSense replaces this with a fully automated pipeline — from tray photo to compliance report — in under 5 seconds.

---

## 🎯 Problem Statement

Institutions like government schools, hospitals, hostels, and corporate canteens serve hundreds of meals daily. Ensuring nutritional adequacy through manual inspection is:
- **Slow** — dietitians cannot check every meal
- **Inconsistent** — results vary between inspectors
- **Disconnected** — attendance and nutrition data are never linked
- **Non-localised** — existing tools use USDA data, which has no data on ragi mudde, jolada rotti, or bisibelebath

NutriSense solves all of these problems in one integrated pipeline.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 1 — INPUT                      │
│   Meal Tray Camera │ Face Camera │ Admin Panel          │
└─────────────────────────┬───────────────────────────────┘
                          │ FastAPI Gateway (JSON)
┌─────────────────────────▼───────────────────────────────┐
│                 LAYER 2 — VISION PIPELINE               │
│   Food Detector (ViT) │ Portion Estimator │ DeepFace    │
└─────────────────────────┬───────────────────────────────┘
                          │ food list, portions, user ID
┌─────────────────────────▼───────────────────────────────┐
│          LAYER 3 — NUTRITION & COMPLIANCE               │
│  Karnataka DB → IFCT 2017 → USDA → Compliance Engine   │
└─────────────────────────┬───────────────────────────────┘
                          │ compliance report
┌─────────────────────────▼───────────────────────────────┐
│              LAYER 4 — AGENTIC AI LAYER                 │
│  Orchestrator Agent │ Suggestion Agent │ Planner Agent  │
└─────────────────────────┬───────────────────────────────┘
                          │ meal logs, menu plans, alerts
┌─────────────────────────▼───────────────────────────────┐
│          LAYER 5 — STORAGE, DASHBOARD & ALERTS          │
│      PostgreSQL │ React Dashboard │ Alert System        │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### ✅ Implemented (Phase 1–4)
- **Multi-item Food Detection** — ViT model fine-tuned on Food-101 with quadrant-splitting for detecting multiple items on a single tray
- **4-Layer Nutrition Lookup** — Priority-based lookup chain:
  1. Karnataka Local DB (ragi mudde, jolada rotti, bisibelebath, sajje rotti...)
  2. IFCT 2017 — NIN Hyderabad (528 Indian foods)
  3. USDA FoodData Central (international fallback)
  4. Default safe estimate
- **Compliance Engine** — Checks against Karnataka MDM Scheme + ICMR-NIN 2020 + FSSAI + WHO standards
- **Student Supplement Tracking** — Tracks egg, banana, milk, chikki distributed separately from tray
- **Tap-to-Select UI API** — Returns structured supplement options for frontend rendering

### 🔄 In Progress (Phase 5–7)
- Face recognition attendance tracking (DeepFace)
- Agentic AI layer (LangChain — orchestrator, suggestion, planner agents)
- React dashboard with compliance trend charts
- PostgreSQL meal logging with user linkage
- Email/SMS alert system for canteen managers

---

## 🗄️ Datasets Used

| Dataset | Source | Purpose |
|---|---|---|
| Food-101 | ETH Zurich (via HuggingFace `nateraw/food`) | Food item classification |
| IFCT 2017 | National Institute of Nutrition, Hyderabad | Indian food nutrition values |
| Karnataka Local Foods | Created by team (based on IFCT + MDM data) | Karnataka-specific staples |
| USDA FoodData Central | USDA Agricultural Research Service | International fallback nutrition |
| Karnataka MDM Scheme | Government of Karnataka | Per-meal compliance thresholds |
| ICMR-NIN RDA 2020 | Indian Council of Medical Research | Daily nutrient requirements |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| Food Detection | Vision Transformer (ViT) via HuggingFace Transformers |
| Face Recognition | DeepFace |
| Nutrition Database | IFCT 2017 + Karnataka Local DB + USDA API |
| Agentic AI | LangChain + Claude/GPT-4 |
| Database | PostgreSQL |
| Frontend | React.js + Chart.js |
| Containerization | Docker Compose |

---

## 📁 Project Structure

```
NutriSense/
├── main.py                      # FastAPI entry point — all endpoints
├── requirements.txt             # Python dependencies
├── .env                         # API keys (not committed)
├── .gitignore
│
├── models/
│   ├── food_detector.py         # ViT food detection + quadrant splitting
│   ├── nutrition_lookup.py      # 4-layer nutrition lookup chain
│   └── face_recognizer.py       # DeepFace attendance tracking
│
├── engine/
│   ├── compliance_engine.py     # Karnataka MDM + ICMR-NIN compliance check
│   └── aggregator.py            # Combines multi-item nutrition into meal total
│
├── agents/
│   ├── orchestrator.py          # LangChain orchestrator agent
│   ├── suggestion_agent.py      # AI corrective recommendations
│   └── planner_agent.py         # Next-day menu planning agent
│
├── database/
│   ├── db.py                    # PostgreSQL connection + SQLAlchemy models
│   └── schemas.py               # Pydantic schemas for request/response
│
└── data/
    ├── karnataka_foods.csv      # Karnataka-specific food nutrition DB
    └── ifct_foods.py            # IFCT 2017 — 528 Indian foods
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Git
- PostgreSQL (for database features)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SIKESOMS/NutriSense.git
cd NutriSense

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
# Create a .env file with:
# USDA_API_KEY=your_usda_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# DATABASE_URL=postgresql://postgres:password@localhost/nutrisense

# 6. Run the server
uvicorn main:app --reload
```

### Access the API
- **API Base:** `http://127.0.0.1:8000`
- **Interactive Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/health`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Server status |
| GET | `/health` | Health check |
| GET | `/supplements/options` | Returns tap-UI supplement options |
| POST | `/detect-food` | Upload tray image → detected food items |
| POST | `/analyze-nutrition` | Upload tray image → food + nutrition data |
| POST | `/analyze-tray` | Upload tray image → full pipeline (food + nutrition + compliance) |
| POST | `/analyze-tray-complete` | Upload tray image + supplements → complete nutritional analysis |

### Example Response — `/analyze-tray-complete`

```json
{
  "filename": "tray_photo.jpg",
  "tray_items": ["chicken_curry", "ragi_mudde", "sambar"],
  "supplements_reported": {"egg": 1, "milk_ml": 200},
  "meal_nutrition_total": {
    "calories": 720.5,
    "protein_g": 32.4,
    "carbs_g": 98.2,
    "fat_g": 18.6,
    "fiber_g": 9.1,
    "iron_mg": 8.3,
    "calcium_mg": 412.0,
    "vitamin_c_mg": 28.5
  },
  "compliance": {
    "compliant": true,
    "compliance_score": 87.5,
    "summary": "7/8 nutrients within Karnataka MDM range",
    "standard": "Karnataka MDM Scheme + ICMR-NIN 2020 + FSSAI"
  }
}
```

---

## 🎯 Compliance Standards Used

| Standard | Source | What it governs |
|---|---|---|
| Karnataka MDM Scheme | Govt. of Karnataka | Per-meal calorie and calcium targets |
| ICMR-NIN RDA 2020 | Indian Council of Medical Research | Protein, carbs, fat, fiber, iron |
| FSSAI Guidelines | Food Safety and Standards Authority of India | Fat limits for school canteens |
| WHO Guidelines | World Health Organization | Vitamin C minimum |

---

## 🌍 SDG Alignment

| SDG | Goal | How NutriSense contributes |
|---|---|---|
| SDG 3 | Good Health and Well-Being | Continuous nutritional monitoring prevents deficiencies |
| SDG 9 | Industry, Innovation and Infrastructure | Open-source AI applied to public health infrastructure |

---

## 👥 Team

| Name | USN | Role |
|---|---|---|
| Aryan Kumar | 1BM23AI037 | System Architecture & Integration |
| Roshanth V | 1BM23AI155 | Food Detection & ML Pipeline |
| S S Gokula Swamy | 1BM23AI158 | Database & Backend |
| Somanath S D | 1BM23AI187 | Agentic AI & Compliance Engine |

**Guide:** Prof. Varsha R, Dept. of Machine Learning, BMSCE

---

## 🏫 Institution

**Department of Machine Learning**
B.M.S. College of Engineering, Bengaluru — 560 019
*(An Autonomous Institute, Affiliated to VTU)*

**Course:** Project Work 2 (24AM7PWPW2)
**Academic Year:** 2026–27

---

## 📚 References

1. Bossard et al. (2014). Food-101 — Mining Discriminative Components with Random Forests. ECCV.
2. National Institute of Nutrition (2017). Indian Food Composition Tables (IFCT 2017). NIN, Hyderabad.
3. ICMR-NIN (2020). Recommended Dietary Allowances for Indians. New Delhi.
4. USDA Agricultural Research Service. FoodData Central. https://fdc.nal.usda.gov/
5. Dosovitskiy et al. (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. ICLR.
6. Taigman et al. (2014). DeepFace: Closing the Gap to Human-Level Performance in Face Verification. CVPR.
7. Chase, H. (2022). LangChain. https://github.com/langchain-ai/langchain
8. Government of Karnataka. Mid-Day Meal Scheme Guidelines. Dept. of Public Instruction.

---

## 📄 License

This project is developed for academic purposes at B.M.S. College of Engineering under Project Work 2 (2026–27).
