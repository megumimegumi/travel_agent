
import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

# Load env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key start: {api_key[:5]}...")

from services.deepseek_client import DeepSeekClient
from agents.recommendation_agent import RecommendationAgent

def test_api():
    print("\nTesting DeepSeek API directly...")
    client = DeepSeekClient()
    try:
        res = client.chat_completion([{"role": "user", "content": "Hello"}], max_tokens=10)
        print("API Response:", res)
        if "error" in res:
            print("❌ API Error")
        else:
            print("✅ API Success")
    except Exception as e:
        print(f"❌ API Exception: {e}")

def test_recommendation():
    print("\nTesting RecommendationAgent...")
    agent = RecommendationAgent()
    try:
        res = agent.recommend({"interests": ["food"]}, "I want to eat spicy food")
        print("Rec Response:", res)
        if res and len(res) > 0:
             print("✅ Recommendation Success")
        else:
             print("❌ Recommendation Empty/Failed")
    except Exception as e:
        print(f"❌ Recommendation Exception: {e}")

if __name__ == "__main__":
    test_api()
    test_recommendation()
