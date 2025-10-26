#!/usr/bin/env python3
"""
Test script to verify the percent_change calculation fix
"""

import pandas as pd
from typing import List

# Copy the fixed functions from the scraper
def analyze_interest_series(values: List[float]) -> dict:
    """Test version of the fixed analyze_interest_series function"""
    if not values:
        return {"trend": "unknown", "percent_change": 0.0, "trend_duration_hours": 0, "sparkline": []}

    # Calculate percent change from first to last value
    first, last = values[0], values[-1]
    percent_change = ((last - first) / max(first, 1)) * 100 if first > 0 else 0.0

    # Determine trend based on percent change
    trend = "steady"
    if percent_change > 15:
        trend = "rising"
    elif percent_change < -15:
        trend = "falling"

    # Calculate consecutive growth hours (looking at recent trend)
    duration = consecutive_growth_hours(values)

    print(f"Interest series analysis: first={first}, last={last}, change={percent_change:.2f}%, trend={trend}")

    return {
        "trend": trend,
        "percent_change": percent_change,
        "trend_duration_hours": duration,
        "sparkline": values[-12:],
    }

def consecutive_growth_hours(values: List[float]) -> int:
    """Calculate consecutive hours of growth/decline from the end of the series."""
    if len(values) < 2:
        return 0
    
    duration = 0
    # Look backwards from the most recent value
    for idx in range(len(values) - 1, 0, -1):
        if values[idx] > values[idx - 1]:
            duration += 1
        else:
            break
    
    # Also check for consecutive decline
    decline_duration = 0
    for idx in range(len(values) - 1, 0, -1):
        if values[idx] < values[idx - 1]:
            decline_duration += 1
        else:
            break
    
    # Return the longer duration (growth or decline)
    return max(duration, decline_duration)

# Test with the actual data from the JSON file
test_cases = [
    {
        "query": "june lockhart",
        "sparkline": [6.0, 6.0, 7.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.0]
    },
    {
        "query": "texas a&m vs lsu", 
        "sparkline": [15.0, 12.0, 11.0, 9.0, 8.0, 7.0, 6.0, 6.0, 6.0, 5.0, 5.0, 4.0]
    },
    {
        "query": "alabama vs south carolina",
        "sparkline": [2.0, 2.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 2.0, 2.0, 2.0, 1.0]
    }
]

print("🧪 Testing percent_change calculation fix:")
print("=" * 50)

for test_case in test_cases:
    query = test_case["query"]
    sparkline = test_case["sparkline"]
    
    print(f"\n📊 Testing: {query}")
    print(f"   Sparkline: {sparkline}")
    
    result = analyze_interest_series(sparkline)
    
    print(f"   ✅ Result:")
    print(f"      Trend: {result['trend']}")
    print(f"      Percent Change: {result['percent_change']:.2f}%")
    print(f"      Duration: {result['trend_duration_hours']} hours")

print(f"\n🎯 Summary:")
print("The fix should now properly calculate percent changes instead of showing 0.0")
print("Trends should be classified as 'rising', 'falling', or 'steady' based on >15% change")
