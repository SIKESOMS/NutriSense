from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import io

class FoodDetector:
    def __init__(self):
        print("Loading food detection model... please wait")
        model_name = "nateraw/food"
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.model.eval()
        self.confidence_threshold = 0.05  # Lower to catch more items
        self.max_items = 5
        print("Food detection model loaded successfully")

    def detect(self, image_bytes: bytes) -> list:
        """
        Detects multiple food items using two strategies:
        1. Full image classification
        2. Quadrant splitting — splits tray into 4 sections
           and classifies each separately
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        all_detections = {}

        # Strategy 1: Full image
        full_results = self._classify_image(image)
        for item in full_results:
            name = item["name"]
            if name not in all_detections:
                all_detections[name] = item

        # Strategy 2: Split into quadrants
        quadrants = self._split_into_quadrants(image)
        for i, quadrant in enumerate(quadrants):
            quad_results = self._classify_image(quadrant, threshold=0.15)
            for item in quad_results:
                name = item["name"]
                if name not in all_detections:
                    # New item found in this quadrant
                    item["detected_in"] = f"quadrant_{i+1}"
                    all_detections[name] = item

        results = list(all_detections.values())
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:self.max_items]

    def _classify_image(self, image: Image.Image,
                        threshold: float = None) -> list:
        """Run model on a single image."""
        if threshold is None:
            threshold = self.confidence_threshold

        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        top5 = torch.topk(probs, 5)

        results = []
        for score, idx in zip(top5.values[0], top5.indices[0]):
            confidence = score.item()
            if confidence >= threshold:
                label = self.model.config.id2label[idx.item()]
                results.append({
                    "name": label,
                    "confidence": round(confidence, 3),
                    "portion_grams": round(150 * confidence, 1),
                    "detected_in": "full_image"
                })
        return results

    def _split_into_quadrants(self, image: Image.Image) -> list:
        """
        Split tray image into 4 quadrants.
        Each quadrant may contain a different food item.
        
        ┌────┬────┐
        │ Q1 │ Q2 │
        ├────┼────┤
        │ Q3 │ Q4 │
        └────┴────┘
        """
        w, h = image.size
        mid_w, mid_h = w // 2, h // 2

        quadrants = [
            image.crop((0,     0,     mid_w, mid_h)),  # Q1 top-left
            image.crop((mid_w, 0,     w,     mid_h)),  # Q2 top-right
            image.crop((0,     mid_h, mid_w, h)),      # Q3 bottom-left
            image.crop((mid_w, mid_h, w,     h)),      # Q4 bottom-right
        ]
        return quadrants