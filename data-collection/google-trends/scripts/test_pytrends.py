#!/usr/bin/env python3
"""
Diagnostic script to test PyTrends functionality
"""

try:
    from pytrends.request import TrendReq
    import pandas as pd
    print("✅ PyTrends imported successfully")
except ImportError as e:
    print(f"❌ PyTrends import failed: {e}")
    exit(1)

def test_pytrends():
    """Test basic PyTrends functionality"""
    print("\n🧪 Testing PyTrends functionality...")
    
    try:
        # Initialize PyTrends
        pytrends = TrendReq(hl='en-US', tz=0, geo='US')
        print("✅ PyTrends initialized successfully")
        
        # Test with a simple query
        test_queries = ["bitcoin", "tesla"]
        print(f"📊 Testing with queries: {test_queries}")
        
        # Build payload
        pytrends.build_payload(test_queries, timeframe='now 1-d', geo='US')
        print("✅ Payload built successfully")
        
        # Get interest over time
        df = pytrends.interest_over_time()
        print(f"✅ Interest data shape: {df.shape}")
        print(f"📈 Columns: {list(df.columns)}")
        
        if not df.empty:
            print("📊 Sample data:")
            print(df.head())
            
            # Test our analysis function
            for query in test_queries:
                if query in df.columns:
                    series = df[query].dropna()
                    if not series.empty:
                        values = series.tolist()
                        first, last = values[0], values[-1]
                        percent_change = ((last - first) / max(first, 1)) * 100 if first > 0 else 0.0
                        print(f"   {query}: {first} → {last} ({percent_change:.2f}% change)")
                    else:
                        print(f"   {query}: Empty series")
                else:
                    print(f"   {query}: Not found in columns")
        else:
            print("❌ Empty interest data")
            
    except Exception as e:
        print(f"❌ PyTrends test failed: {e}")
        return False
    
    return True

def test_related_queries():
    """Test related queries functionality"""
    print("\n🔍 Testing related queries...")
    
    try:
        pytrends = TrendReq(hl='en-US', tz=0, geo='US')
        pytrends.build_payload(["bitcoin"], timeframe='now 7-d', geo='US')
        response = pytrends.related_queries()
        
        print(f"✅ Related queries response: {type(response)}")
        for query, payload in response.items():
            print(f"   {query}: {payload}")
            
    except Exception as e:
        print(f"❌ Related queries test failed: {e}")

if __name__ == "__main__":
    print("🔧 PyTrends Diagnostic Tool")
    print("=" * 40)
    
    success = test_pytrends()
    test_related_queries()
    
    if success:
        print("\n✅ PyTrends is working correctly")
        print("The issue might be with rate limiting or the specific queries being used")
    else:
        print("\n❌ PyTrends has issues that need to be resolved")
