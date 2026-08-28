import csv
import os
import requests
from dotenv import load_dotenv
from data.ifct_foods import IFCT_DATABASE

load_dotenv()

class NutritionLookup:
    def __init__(self):
        self.usda_api_key = os.getenv("USDA_API_KEY", "DEMO_KEY")
        self.karnataka_db = self._load_karnataka_db()
        print(f"Karnataka DB loaded: {len(self.karnataka_db)} foods")
        print(f"IFCT DB loaded: {len(IFCT_DATABASE)} foods")

    def _load_karnataka_db(self) -> dict:
        """Load Karnataka local foods from CSV."""
        db = {}
        csv_path = "data/karnataka_foods.csv"
        if not os.path.exists(csv_path):
            return db
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Store by main name
                db[row['food_name']] = {
                    "source": "Karnataka Local DB",
                    "region": row['region'],
                    "calories":     float(row['calories']),
                    "protein_g":    float(row['protein_g']),
                    "carbs_g":      float(row['carbs_g']),
                    "fat_g":        float(row['fat_g']),
                    "fiber_g":      float(row['fiber_g']),
                    "iron_mg":      float(row['iron_mg']),
                    "calcium_mg":   float(row['calcium_mg']),
                    "vitamin_c_mg": float(row['vitamin_c_mg']),
                }
                # Also store by aliases
                for alias in row['aliases'].split('_'):
                    db[alias] = db[row['food_name']]
        return db

    def lookup(self, food_name: str) -> dict:
        """
        4-layer lookup:
        1. Karnataka local DB (most relevant for project)
        2. IFCT 2017 - NIN Hyderabad (Indian standard)
        3. USDA FoodData Central (international fallback)
        4. Default estimate
        """
        clean_name = food_name.lower().replace(" ", "_").replace("-", "_")

        # Layer 1: Karnataka Local DB
        result = self._check_karnataka(clean_name)
        if result:
            return result

        # Layer 2: IFCT 2017 (NIN Hyderabad)
        result = self._check_ifct(clean_name)
        if result:
            return result

        # Layer 3: USDA API
        result = self._check_usda(food_name)
        if result:
            return result

        # Layer 4: Default
        return self._default(food_name)

    def _check_karnataka(self, food_name: str) -> dict | None:
        """Check Karnataka local database first."""
        # Direct match
        if food_name in self.karnataka_db:
            data = self.karnataka_db[food_name].copy()
            data["food_name"] = food_name
            data["lookup_source"] = "Karnataka Local DB"
            return data

        # Partial match (e.g. "chicken_curry" matches "chicken")
        for key in self.karnataka_db:
            if key in food_name or food_name in key:
                data = self.karnataka_db[key].copy()
                data["food_name"] = food_name
                data["lookup_source"] = "Karnataka Local DB (partial match)"
                return data
        return None

    def _check_ifct(self, food_name: str) -> dict | None:
        """Check IFCT 2017 database."""
        # Direct match
        if food_name in IFCT_DATABASE:
            data = IFCT_DATABASE[food_name].copy()
            data["food_name"] = food_name
            data["lookup_source"] = "IFCT 2017 - NIN Hyderabad"
            return data

        # Partial match
        for key in IFCT_DATABASE:
            if key in food_name or food_name in key:
                data = IFCT_DATABASE[key].copy()
                data["food_name"] = food_name
                data["lookup_source"] = "IFCT 2017 - NIN Hyderabad (partial match)"
                return data
        return None

    def _check_usda(self, food_name: str) -> dict | None:
        """Check USDA as international fallback."""
        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": food_name,
                "api_key": self.usda_api_key,
                "pageSize": 1,
                "dataType": "Foundation,SR Legacy"
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            if not data.get("foods"):
                return None

            food = data["foods"][0]
            nutrients = {n["nutrientName"]: n["value"]
                        for n in food.get("foodNutrients", [])}

            return {
                "food_name": food_name,
                "lookup_source": "USDA FoodData Central",
                "calories":     nutrients.get("Energy", 200),
                "protein_g":    nutrients.get("Protein", 8),
                "carbs_g":      nutrients.get("Carbohydrate, by difference", 30),
                "fat_g":        nutrients.get("Total lipid (fat)", 5),
                "fiber_g":      nutrients.get("Fiber, total dietary", 2),
                "iron_mg":      nutrients.get("Iron, Fe", 1),
                "calcium_mg":   nutrients.get("Calcium, Ca", 50),
                "vitamin_c_mg": nutrients.get("Vitamin C, total ascorbic acid", 5),
            }
        except Exception:
            return None

    def _default(self, food_name: str) -> dict:
        """Final fallback with safe estimates."""
        return {
            "food_name": food_name,
            "lookup_source": "Default estimate",
            "calories": 200, "protein_g": 8,
            "carbs_g": 30, "fat_g": 5,
            "fiber_g": 2, "iron_mg": 1,
            "calcium_mg": 50, "vitamin_c_mg": 5,
        }