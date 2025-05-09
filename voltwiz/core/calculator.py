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
                - priority (str): "max_discount" or "time_specific"
                - discount_window (tuple): (start_hour, end_hour) if priority is "time_specific"
                - min_discount_pct (float): Minimum acceptable discount percentage
        
        Returns:
            The recommended Provider object or None if no suitable provider is found
        """
        # 1. Filter out plans the user can't take
        valid_providers = [
            p for p in self.providers
            if (not p.requires_smart_meter or user_prefs["has_smart_meter"]) and
               p.discount_pct >= user_prefs["min_discount_pct"]
        ]

        if not valid_providers:
            return None

        # 2. Score according to priority
        def score_provider(provider):
            if user_prefs["priority"] == "max_discount":
                return provider.discount_pct
            else:
                # time_specific: check overlap of plan hours with desired window
                win_start, win_end = user_prefs["discount_window"]
                p_hours = provider.hours
                
                if p_hours is None:
                    # all-day plans get full score
                    return provider.discount_pct
                    
                # compute overlap duration (simple version)
                ps, pe = p_hours
                
                # normalize overnight windows
                if pe <= ps:
                    pe += 24
                if win_end <= win_start:
                    win_end += 24
                    
                overlap = max(0, min(pe, win_end) - max(ps, win_start))
                
                # combine overlap (hrs) and discount pct
                return overlap * provider.discount_pct

        # 3. Pick the highest scored plan
        return max(valid_providers, key=score_provider)

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
            hours_desc = "All day"
        else:
            start, end = provider.hours
            hours_desc = f"{start}:00-{end}:00"
            
        # Calculate the score for comparison
        if user_prefs["priority"] == "max_discount":
            score_type = "discount percentage"
            score_value = f"{provider.discount_pct}%"
        else:
            # For time-specific, show both discount and hours
            score_type = "discount during your preferred hours"
            score_value = f"{provider.discount_pct}% ({hours_desc})"
        
        # Calculate potential savings compared to average discount
        avg_discount = sum(p.discount_pct for p in self.providers) / len(self.providers)
        savings_vs_avg = provider.discount_pct - avg_discount
        
        # Format the recommendation message
        recommendation = (
            f"✅ *Recommended Provider: {provider.vendor} - {provider.name}*\n\n"
            f"📊 *Plan Details:*\n"
            f"- Discount: {provider.discount_pct}%\n"
            f"- Hours: {hours_desc}\n"
            f"- Smart Meter Required: {'Yes' if provider.requires_smart_meter else 'No'}\n\n"
            f"💰 *Why This Plan:*\n"
            f"- Best {score_type}: {score_value}\n"
            f"- {'Better than average by' if savings_vs_avg > 0 else 'Compared to average:'} {abs(savings_vs_avg):.1f}%\n\n"
            f"ℹ️ *Next Steps:*\n"
            f"- Contact {provider.vendor} to sign up for the '{provider.name}' plan\n"
            f"- {'Make sure to install a smart meter' if provider.requires_smart_meter else 'No smart meter required'}\n"
            f"- {'Optimize your usage during discount hours' if provider.hours is not None else 'Enjoy discounts all day'}"
        )
        
        return recommendation
