import pytest
from src.core.calculator import Provider, ProviderCalculator

@pytest.fixture
def sample_providers():
    return [
        {
            "name": "GreenPower Plus",
            "vendor": "Green Energy Co",
            "discount_pct": 15.0,
            "hours": None,  # All day
            "requires_smart_meter": True
        },
        {
            "name": "Basic Energy",
            "vendor": "Basic Power",
            "discount_pct": 10.0,
            "hours": [18, 22],  # Evening hours
            "requires_smart_meter": False
        }
    ]

@pytest.fixture
def calculator(sample_providers, tmp_path):
    # Create a temporary providers.json file
    import json
    providers_file = tmp_path / "providers.json"
    with open(providers_file, 'w') as f:
        json.dump({"providers": sample_providers}, f)
    return ProviderCalculator(str(providers_file))

def test_provider_initialization(sample_providers):
    provider = Provider(sample_providers[0])
    assert provider.name == "GreenPower Plus"
    assert provider.vendor == "Green Energy Co"
    assert provider.discount_pct == 15.0
    assert provider.hours is None
    assert provider.requires_smart_meter is True

def test_provider_str_representation(sample_providers):
    provider = Provider(sample_providers[0])
    assert str(provider) == "Green Energy Co - GreenPower Plus (15.0% discount, All day)"

def test_get_recommendation_max_discount(calculator):
    user_prefs = {
        "has_smart_meter": True,
        "priority": "max_discount",
        "min_discount_pct": 5.0
    }
    provider = calculator.get_recommendation(user_prefs)
    assert provider.name == "GreenPower Plus"
    assert provider.discount_pct == 15.0

def test_get_recommendation_time_specific(calculator):
    user_prefs = {
        "has_smart_meter": False,
        "priority": "time_specific",
        "discount_window": (18, 22),
        "min_discount_pct": 5.0
    }
    provider = calculator.get_recommendation(user_prefs)
    assert provider.name == "Basic Energy"
    assert provider.hours == [18, 22]

def test_no_suitable_provider(calculator):
    user_prefs = {
        "has_smart_meter": False,
        "priority": "max_discount",
        "min_discount_pct": 20.0  # Higher than any available discount
    }
    provider = calculator.get_recommendation(user_prefs)
    assert provider is None

def test_format_recommendation(calculator):
    provider = Provider({
        "name": "Test Plan",
        "vendor": "Test Vendor",
        "discount_pct": 15.0,
        "hours": [18, 22],
        "requires_smart_meter": True
    })
    user_prefs = {
        "has_smart_meter": True,
        "priority": "time_specific",
        "discount_window": (18, 22),
        "min_discount_pct": 10.0
    }
    recommendation = calculator.format_recommendation(provider, user_prefs)
    assert "Test Vendor - Test Plan" in recommendation
    assert "15.0%" in recommendation
    assert "18:00-22:00" in recommendation 