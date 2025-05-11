import json
from typing import Dict, Optional
from pathlib import Path

class Provider:
    """
    Represents an electricity provider with its plan details.
    """
    def __init__(self, data: Dict):
        self.name = data['name']
        self.vendor = data['vendor']
        self.discount_pct = data['discount_pct']
        self.hours = data['hours']  # None for all-day or Tuple[int, int] for specific hours
        self.requires_smart_meter = data['requires_smart_meter']

    def __str__(self) -> str:
        hours_str = "All day" if self.hours is None else f"{self.hours[0]}:00-{self.hours[1]}:00"
        return f"{self.vendor} - {self.name} ({self.discount_pct}% discount, {hours_str})"

class ProviderCalculator:
    """
    Calculator for recommending the best electricity provider based on user preferences.
    """
    def __init__(self, providers_file: str = None):
        if providers_file is None:
            # Use default path relative to the package
            package_dir = Path(__file__).parent.parent
            providers_file = package_dir / 'data' / 'providers.json'
        
        with open(providers_file, 'r') as f:
            data = json.load(f)
        self.providers = [Provider(p) for p in data["providers"]]

    def get_recommendation(self, user_prefs: Dict) -> Optional[Provider]:
        """
        Recommend the best electricity provider based on user preferences.
        
        Args:
            user_prefs: Dictionary with keys:
                - has_smart_meter (bool): Whether the user has a smart meter
                - discount_type (str): "fixed" or "variable"
                - time_preference (str): "day" or "night" (only if discount_type is "variable")
                - vendor (str): "hot", "amisragaz", or "none"
        
        Returns:
            The recommended Provider object or None if no suitable provider is found
        """
        # 1. Filter out plans the user can't take
        valid_providers = [
            p for p in self.providers
            if (not p.requires_smart_meter or user_prefs["has_smart_meter"])
        ]

        if not valid_providers:
            return None

        # 2. Filter by discount type
        if user_prefs["discount_type"] == "fixed":
            # For fixed discount, prefer plans with no specific hours
            valid_providers = [p for p in valid_providers if p.hours is None]
        else:  # variable discount
            # For variable discount, filter by time preference
            if user_prefs["time_preference"] == "day":
                valid_providers = [p for p in valid_providers if p.hours == [7, 17]]
            else:  # night
                valid_providers = [p for p in valid_providers if p.hours == [23, 7]]

        if not valid_providers:
            return None

        # 3. Filter by vendor if specified
        if user_prefs["vendor"] != "none":
            valid_providers = [p for p in valid_providers if p.vendor.lower() == user_prefs["vendor"].lower()]

        if not valid_providers:
            return None

        # 4. Pick the plan with the highest discount
        return max(valid_providers, key=lambda p: p.discount_pct)

    def format_recommendation(self, provider: Provider, user_prefs: Dict) -> str:
        """
        Format the recommendation as a user-friendly message.
        
        Args:
            provider: The recommended Provider object
            user_prefs: The user preferences dictionary
            
        Returns:
            A formatted string with the recommendation details
        """
        # Determine hours description
        if provider.hours is None:
            hours_desc = "כל היום"
        else:
            start, end = provider.hours
            hours_desc = f"{start}:00-{end}:00"
            
        # Calculate potential savings compared to average discount
        avg_discount = sum(p.discount_pct for p in self.providers) / len(self.providers)
        savings_vs_avg = provider.discount_pct - avg_discount
        
        # Format the recommendation message
        recommendation = (
            f"✅ *הספק המומלץ: {provider.vendor} - {provider.name}*\n\n"
            f"📊 *פרטי התוכנית:*\n"
            f"- הנחה: {provider.discount_pct}%\n"
            f"- שעות: {hours_desc}\n"
            f"- דורש שעון חכם: {'כן' if provider.requires_smart_meter else 'לא'}\n\n"
            f"💰 *יתרונות התוכנית:*\n"
            f"- הנחה גבוהה יותר מהממוצע ב-{abs(savings_vs_avg):.1f}%\n"
            f"- {'הנחה קבועה' if provider.hours is None else 'הנחה בשעות מועדפות'}\n\n"
            f"ℹ️ *הצעדים הבאים:*\n"
            f"- צור קשר עם {provider.vendor} להרשמה לתוכנית '{provider.name}'\n"
            f"- {'התקן שעון חכם' if provider.requires_smart_meter else 'אין צורך בשעון חכם'}\n"
            f"- {'התאם את צריכת החשמל לשעות ההנחה' if provider.hours is not None else 'הנחה קבועה לאורך כל היום'}"
        )
        
        return recommendation
