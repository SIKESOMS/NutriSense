from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
from models.food_detector import FoodDetector
from models.nutrition_lookup import NutritionLookup
from engine.aggregator import NutritionAggregator
from engine.compliance_engine import ComplianceEngine

app = FastAPI(title="NutriSense API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing NutriSense...")
detector     = FoodDetector()
nutrition    = NutritionLookup()
aggregator   = NutritionAggregator()
compliance   = ComplianceEngine()

@app.get("/")
def root():
    return {"message": "NutriSense is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect-food")
async def detect_food(file: UploadFile = File(...)):
    image_bytes = await file.read()
    food_items = detector.detect(image_bytes)
    return {
        "filename": file.filename,
        "detected_items": food_items,
        "item_count": len(food_items)
    }

@app.post("/analyze-nutrition")
async def analyze_nutrition(file: UploadFile = File(...)):
    image_bytes = await file.read()
    food_items = detector.detect(image_bytes)
    if not food_items:
        return {"error": "No food detected"}

    nutrition_results = []
    for item in food_items:
        nutrition_data = nutrition.lookup(item["name"])
        portion = item["portion_grams"]
        scale = portion / 100
        nutrition_results.append({
            "food": item["name"],
            "confidence": item["confidence"],
            "portion_grams": portion,
            "lookup_source": nutrition_data["lookup_source"],
            "nutrition_scaled": {
                k: round(nutrition_data[k] * scale, 1)
                for k in ["calories","protein_g","carbs_g","fat_g",
                          "fiber_g","iron_mg","calcium_mg","vitamin_c_mg"]
            }
        })

    return {
        "filename": file.filename,
        "items_analyzed": len(nutrition_results),
        "results": nutrition_results
    }

@app.post("/analyze-tray")
async def analyze_tray(file: UploadFile = File(...)):
    """
    FULL PIPELINE:
    Image → Food Detection → Nutrition Lookup → 
    Aggregation → Compliance Check
    """
    image_bytes = await file.read()

    # Step 1: Detect food
    food_items = detector.detect(image_bytes)
    if not food_items:
        return {"error": "No food detected in image"}

    # Step 2: Nutrition lookup for each item
    nutrition_results = []
    for item in food_items:
        nutrition_data = nutrition.lookup(item["name"])
        portion = item["portion_grams"]
        scale = portion / 100
        nutrition_results.append({
            "food": item["name"],
            "confidence": item["confidence"],
            "portion_grams": portion,
            "lookup_source": nutrition_data["lookup_source"],
            "nutrition_scaled": {
                k: round(nutrition_data[k] * scale, 1)
                for k in ["calories","protein_g","carbs_g","fat_g",
                          "fiber_g","iron_mg","calcium_mg","vitamin_c_mg"]
            }
        })

    # Step 3: Aggregate all items into one meal total
    meal_nutrition = aggregator.aggregate(nutrition_results)

    # Step 4: Check compliance against Karnataka MDM thresholds
    compliance_report = compliance.check(meal_nutrition)

    return {
        "filename": file.filename,
        "tray_items": [r["food"] for r in nutrition_results],
        "meal_nutrition_total": meal_nutrition,
        "compliance": compliance_report
    }

@app.post("/analyze-tray-complete")
async def analyze_tray_complete(
    file: UploadFile = File(...),
    supplements: Optional[str] = Form(default="{}")
):
    """
    COMPLETE PIPELINE including student supplements.
    
    supplements: JSON string of additional items student consumed
    Example: {"egg": 1, "banana": 1, "milk_ml": 200, "chikki": 1}
    """
    image_bytes = await file.read()

    # Parse supplements input
    try:
        supplement_data = json.loads(supplements)
    except:
        supplement_data = {}

    # Step 1: Detect food from tray image
    food_items = detector.detect(image_bytes)
    if not food_items:
        return {"error": "No food detected in image"}

    # Step 2: Nutrition lookup for tray items
    nutrition_results = []
    for item in food_items:
        nutrition_data = nutrition.lookup(item["name"])
        portion = item["portion_grams"]
        scale = portion / 100
        nutrition_results.append({
            "food": item["name"],
            "source": "tray_camera",
            "confidence": item["confidence"],
            "portion_grams": portion,
            "lookup_source": nutrition_data["lookup_source"],
            "nutrition_scaled": {
                k: round(nutrition_data[k] * scale, 1)
                for k in ["calories","protein_g","carbs_g","fat_g",
                          "fiber_g","iron_mg","calcium_mg","vitamin_c_mg"]
            }
        })

    # Step 3: Add supplement nutrition
    # Karnataka MDM common supplements with nutrition per unit
    SUPPLEMENT_NUTRITION = {
        "egg": {
            "calories": 78, "protein_g": 6.3, "carbs_g": 0.6,
            "fat_g": 5.3, "fiber_g": 0.0, "iron_mg": 1.0,
            "calcium_mg": 50.0, "vitamin_c_mg": 0.0,
            "unit": "1 egg (50g)"
        },
        "banana": {
            "calories": 89, "protein_g": 1.1, "carbs_g": 23.0,
            "fat_g": 0.3, "fiber_g": 2.6, "iron_mg": 0.3,
            "calcium_mg": 5.0, "vitamin_c_mg": 8.7,
            "unit": "1 banana (100g)"
        },
        "milk_ml": {
            "calories": 0.67, "protein_g": 0.032, "carbs_g": 0.044,
            "fat_g": 0.041, "fiber_g": 0.0, "iron_mg": 0.002,
            "calcium_mg": 1.2, "vitamin_c_mg": 0.02,
            "unit": "per ml"
        },
        "chikki": {
            "calories": 450, "protein_g": 14.0, "carbs_g": 55.0,
            "fat_g": 20.0, "fiber_g": 4.0, "iron_mg": 2.5,
            "calcium_mg": 60.0, "vitamin_c_mg": 0.0,
            "unit": "1 piece (30g)"
        }
    }

    supplement_results = []
    for supplement, quantity in supplement_data.items():
        if supplement in SUPPLEMENT_NUTRITION and quantity > 0:
            s = SUPPLEMENT_NUTRITION[supplement]
            # Multiply by quantity
            supplement_results.append({
                "food": supplement,
                "source": "student_reported",
                "quantity": quantity,
                "nutrition_scaled": {
                    "calories":     round(s["calories"] * quantity, 1),
                    "protein_g":    round(s["protein_g"] * quantity, 1),
                    "carbs_g":      round(s["carbs_g"] * quantity, 1),
                    "fat_g":        round(s["fat_g"] * quantity, 1),
                    "fiber_g":      round(s["fiber_g"] * quantity, 1),
                    "iron_mg":      round(s["iron_mg"] * quantity, 1),
                    "calcium_mg":   round(s["calcium_mg"] * quantity, 1),
                    "vitamin_c_mg": round(s["vitamin_c_mg"] * quantity, 1),
                }
            })

    # Step 4: Aggregate tray + supplements together
    all_items = nutrition_results + supplement_results
    meal_nutrition = aggregator.aggregate(all_items)

    # Step 5: Compliance check
    compliance_report = compliance.check(meal_nutrition)

    return {
        "filename": file.filename,
        "tray_items": [r["food"] for r in nutrition_results],
        "supplements_reported": supplement_data,
        "meal_nutrition_total": meal_nutrition,
        "compliance": compliance_report,
        "breakdown": {
            "from_tray": nutrition_results,
            "from_supplements": supplement_results
        }
    }

@app.get("/supplements/options")
def get_supplement_options():
    """
    Returns available supplement options for the student UI.
    Frontend uses this to build the tap-to-select screen.
    """
    return {
        "supplements": [
            {
                "id": "egg",
                "label": "Egg",
                "emoji": "🥚",
                "type": "counter",
                "options": [0, 1, 2],
                "default": 0,
                "nutrition_per_unit": {
                    "calories": 78, "protein_g": 6.3,
                    "calcium_mg": 50, "iron_mg": 1.0
                }
            },
            {
                "id": "banana",
                "label": "Banana",
                "emoji": "🍌",
                "type": "counter",
                "options": [0, 1, 2],
                "default": 0,
                "nutrition_per_unit": {
                    "calories": 89, "protein_g": 1.1,
                    "vitamin_c_mg": 8.7, "fiber_g": 2.6
                }
            },
            {
                "id": "milk_ml",
                "label": "Milk",
                "emoji": "🥛",
                "type": "toggle",
                "options": [0, 200],
                "option_labels": ["No", "Yes (200ml)"],
                "default": 0,
                "nutrition_per_unit": {
                    "calories": 134, "protein_g": 6.4,
                    "calcium_mg": 240, "fat_g": 8.2
                }
            },
            {
                "id": "chikki",
                "label": "Chikki",
                "emoji": "🍬",
                "type": "toggle",
                "options": [0, 1],
                "option_labels": ["No", "Yes"],
                "default": 0,
                "nutrition_per_unit": {
                    "calories": 135, "protein_g": 4.2,
                    "calcium_mg": 18, "iron_mg": 0.75
                }
            }
        ],
        "instruction": "Tap what you received today",
        "scheme": "Karnataka Mid-Day Meal Scheme"
    }

