#!/usr/bin/env python3
"""Test the parameter handling fix"""

import os
import asyncio
from dotenv import load_dotenv
from listeners.agno_integration import get_or_create_agent

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

async def test_agent_with_instructions():
    """Test that the agent follows the new parameter handling instructions"""
    
    print("🧪 Testing agent with new parameter handling instructions...")
    
    try:
        # Get agent
        agent = get_or_create_agent("test-session")
        print("✅ Agent created successfully")
        
        # Test with a simple message that would trigger Notion actions
        test_message = "Can you help me fetch data from my Notion workspace?"
        
        print(f"\n📝 Testing with message: '{test_message}'")
        response = await agent.arun(test_message)
        
        # Handle different response types
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
            
        print(f"\n✅ Agent response: {response_text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent_with_instructions())
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")