class NutritionAggregator:
    """Combines nutrition from multiple food items into one meal total."""

    def aggregate(self, nutrition_results: list) -> dict:
        """
        Takes list of per-food nutrition results,
        returns total meal nutrition.
        """
        totals = {
            "calories": 0, "protein_g": 0, "carbs_g": 0,
            "fat_g": 0, "fiber_g": 0, "iron_mg": 0,
            "calcium_mg": 0, "vitamin_c_mg": 0
        }

        for item in nutrition_results:
            scaled = item.get("nutrition_scaled", {})
            for nutrient in totals:
                totals[nutrient] += scaled.get(nutrient, 0)

        return {k: round(v, 1) for k, v in totals.items()}