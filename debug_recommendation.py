
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agents.recommendation_agent import RecommendationAgent

def test():
    print("Initializing Agent...")
    agent = RecommendationAgent()
    
    print("Calling recommend...")
    start = time.time()
    try:
        res = agent.recommend(
            {"age_group": "青年", "interests": ["自然风光"]}, 
            "推荐3个地方"
        )
        end = time.time()
        print(f"Result: {res}")
        print(f"Time taken: {end - start:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
