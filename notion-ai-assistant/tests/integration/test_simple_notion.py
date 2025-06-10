#!/usr/bin/env python3
"""Simple test of Notion functionality without Slack"""

import asyncio
import os
from dotenv import load_dotenv
from listeners.agno_integration import get_or_create_agent

load_dotenv()

async def test_notion_direct():
    """Test Notion tools directly with the agent"""
    print("🧪 Testing Notion AI Assistant directly...\n")
    
    # Create agent
    agent = get_or_create_agent("test-session")
    print("✅ Agent created\n")
    
    # Test queries
    test_queries = [
        "What databases do I have in my Notion workspace?",
        "List all my Notion databases",
        "Show me databases in Notion",
    ]
    
    for query in test_queries:
        print(f"📝 Query: {query}")
        print("-" * 50)
        
        try:
            response = await agent.arun(query)
            print(f"✅ Response:\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        print("=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_notion_direct())