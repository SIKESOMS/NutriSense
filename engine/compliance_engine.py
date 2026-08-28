class ComplianceEngine:
    """
    Checks meal nutrition against Karnataka Mid-Day Meal Scheme targets.
    Sources:
    - Karnataka MDM Scheme (Class 6-8, per meal)
    - ICMR-NIN Recommended Dietary Allowances 2020
    - FSSAI Dietary Guidelines for School Canteens
    """

    # Per meal targets (approximately 1/3 of daily requirement)
    KARNATAKA_MDM_THRESHOLDS = {
        "calories":     {"min": 600,  "max": 900,  "unit": "kcal",
                         "source": "Karnataka MDM Scheme"},
        "protein_g":    {"min": 20,   "max": 40,   "unit": "g",
                         "source": "ICMR-NIN 2020"},
        "carbs_g":      {"min": 80,   "max": 150,  "unit": "g",
                         "source": "ICMR-NIN 2020"},
        "fat_g":        {"min": 15,   "max": 40,   "unit": "g",
                         "source": "FSSAI Guidelines"},
        "fiber_g":      {"min": 8,    "max": 30,   "unit": "g",
                         "source": "ICMR-NIN 2020"},
        "iron_mg":      {"min": 5,    "max": 15,   "unit": "mg",
                         "source": "ICMR-NIN 2020"},
        "calcium_mg":   {"min": 300,  "max": 600,  "unit": "mg",
                         "source": "Karnataka MDM Scheme"},
        "vitamin_c_mg": {"min": 25,   "max": 200,  "unit": "mg",
                         "source": "WHO Guidelines"},
    }

    def check(self, meal_nutrition: dict) -> dict:
        """
        Compare meal nutrition against thresholds.
        Returns full compliance report.
        """
        deficits = []
        excesses = []
        passed = []

        for nutrient, threshold in self.KARNATAKA_MDM_THRESHOLDS.items():
            actual = meal_nutrition.get(nutrient, 0)
            min_val = threshold["min"]
            max_val = threshold["max"]
            unit = threshold["unit"]
            source = threshold["source"]

            if actual < min_val:
                gap_percent = round(((min_val - actual) / min_val) * 100, 1)
                deficits.append({
                    "nutrient": nutrient,
                    "actual": actual,
                    "required_min": min_val,
                    "unit": unit,
                    "gap": round(min_val - actual, 1),
                    "gap_percent": gap_percent,
                    "standard_source": source,
                    "severity": "high" if gap_percent > 50 else "medium"
                })
            elif actual > max_val:
                excesses.append({
                    "nutrient": nutrient,
                    "actual": actual,
                    "allowed_max": max_val,
                    "unit": unit,
                    "excess": round(actual - max_val, 1),
                    "standard_source": source
                })
            else:
                passed.append(nutrient)

        total = len(self.KARNATAKA_MDM_THRESHOLDS)
        score = round((len(passed) / total) * 100, 1)

        return {
            "compliant": len(deficits) == 0 and len(excesses) == 0,
            "compliance_score": score,
            "summary": f"{len(passed)}/{total} nutrients within Karnataka MDM range",
            "passed_nutrients": passed,
            "deficits": deficits,
            "excesses": excesses,
            "standard": "Karnataka MDM Scheme + ICMR-NIN 2020 + FSSAI"
        }