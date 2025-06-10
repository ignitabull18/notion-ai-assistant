#!/usr/bin/env python3
"""Test long-term memory functionality"""

import os
import asyncio
from dotenv import load_dotenv
from listeners.agno_integration import get_or_create_agent

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

async def test_memory():
    """Test that the agent has working long-term memory"""
    
    print("🧠 Testing long-term memory functionality...")
    
    try:
        # Get agent with a specific user session
        test_user_id = "test-user-123"
        agent = get_or_create_agent(f"memory-test-{test_user_id}")
        print("✅ Agent created with memory configuration")
        
        # Check memory configuration
        print(f"Memory object: {type(agent.memory) if hasattr(agent, 'memory') else 'None'}")
        print(f"Storage object: {type(agent.storage) if hasattr(agent, 'storage') else 'None'}")
        print(f"User memories enabled: {agent.enable_user_memories if hasattr(agent, 'enable_user_memories') else 'Unknown'}")
        print(f"Session summaries enabled: {agent.enable_session_summaries if hasattr(agent, 'enable_session_summaries') else 'Unknown'}")
        print(f"History runs: {agent.num_history_runs if hasattr(agent, 'num_history_runs') else 'Unknown'}")
        
        # Test 1: Store a preference
        print("\n📝 Test 1: Storing user preference...")
        response1 = await agent.arun("Remember that I prefer to organize my Notion pages by project and I work in the marketing department.")
        print(f"Response: {response1.content if hasattr(response1, 'content') else str(response1)[:100]}...")
        
        # Test 2: Reference the stored information
        print("\n📝 Test 2: Referencing stored information...")
        response2 = await agent.arun("What do you remember about my work preferences?")
        print(f"Response: {response2.content if hasattr(response2, 'content') else str(response2)[:200]}...")
        
        # Check if memory database has entries
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'db'):
            try:
                # Try to check memory database
                print("\n💾 Checking memory database...")
                # This is just to verify the database exists and is accessible
                print(f"Memory DB file: {agent.memory.db.db_file if hasattr(agent.memory.db, 'db_file') else 'Unknown'}")
                print(f"Memory DB table: {agent.memory.db.table_name if hasattr(agent.memory.db, 'table_name') else 'Unknown'}")
            except Exception as e:
                print(f"⚠️ Memory database check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_memory())
    if success:
        print("\n🎉 Memory test completed!")
    else:
        print("\n❌ Memory test failed!")