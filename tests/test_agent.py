import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.planning_agent import PlanningAgent

async def run():
    agent = PlanningAgent()
    res = await agent.run("我要去北京旅游三天")
    print(res)

asyncio.run(run())
