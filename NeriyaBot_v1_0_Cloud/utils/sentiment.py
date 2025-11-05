import requests
import logging

class MarketSentiment:
    """
    מודול לקבלת מצב הרגש בשוק (Fear & Greed Index)
    """

    def __init__(self):
        self.api_url = "https://api.alternative.me/fng/"

    def get_fear_greed_index(self):
        try:
            response = requests.get(self.api_url, params={"limit": 1, "format": "json"})
            data = response.json()
            value = int(data["data"][0]["value"])
            classification = data["data"][0]["value_classification"]
            logging.info(f"📊 Fear & Greed Index: {value} ({classification})")
            return value, classification
        except Exception as e:
            logging.error(f"❌ שגיאה בקבלת מדד הפחד/תאווה: {e}")
            return 50, "Neutral"  # ערך ברירת מחדל במקרה של כשל API

    def get_adjusted_risk(self, base_risk=1.0):
        """
        מחשב אחוז סיכון חדש לפי מצב השוק:
        - פחד קיצוני -> סיכון נמוך יותר
        - תאווה קיצונית -> גם סיכון נמוך יותר
        """
        index, mood = self.get_fear_greed_index()

        if index <= 25:
            new_risk = base_risk * 0.5
            msg = f"😨 פחד קיצוני ({index}) – סיכון מופחת ל-{new_risk:.2f}%"
        elif index >= 75:
            new_risk = base_risk * 0.7
            msg = f"😈 תאווה קיצונית ({index}) – סיכון מופחת ל-{new_risk:.2f}%"
        else:
            new_risk = base_risk
            msg = f"🙂 שוק רגוע ({index}) – סיכון רגיל ({new_risk:.2f}%)"

        logging.info(msg)
        return round(new_risk, 2), msg
