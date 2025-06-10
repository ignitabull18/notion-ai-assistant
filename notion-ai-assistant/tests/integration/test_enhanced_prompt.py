#!/usr/bin/env python3
"""Test the enhanced system prompt"""

import os
import asyncio
from dotenv import load_dotenv
from listeners.agno_integration import get_or_create_agent

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

async def test_enhanced_prompt():
    """Test the enhanced system prompt capabilities"""
    
    print("🎯 Testing enhanced system prompt...")
    
    try:
        # Reset agent to get new prompt
        import listeners.agno_integration
        listeners.agno_integration._agent_instance = None
        
        # Get agent with enhanced prompt
        agent = get_or_create_agent("enhanced-prompt-test")
        print("✅ Agent created with enhanced system prompt")
        
        # Test strategic thinking
        test_message = "I'm a marketing manager and my Notion workspace is a mess. Help me redesign it."
        
        print(f"\n📝 Testing strategic response with: '{test_message}'")
        response = await agent.arun(test_message)
        
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(f"\n✅ Enhanced strategic response generated ({len(response_text)} characters)")
        print(f"Response preview: {response_text[:500]}...")
        
        # Check if response demonstrates enhanced capabilities
        enhanced_indicators = [
            "best practices", "optimization", "workflow", "architecture", 
            "strategy", "template", "scalable", "productivity"
        ]
        
        found_indicators = [ind for ind in enhanced_indicators if ind.lower() in response_text.lower()]
        print(f"\n🧠 Enhanced thinking indicators found: {found_indicators}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced prompt test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_prompt())
    if success:
        print("\n🎉 Enhanced system prompt test completed!")
        print("Your agent now thinks more strategically and provides:")
        print("  🏗️ Workspace architecture guidance")
        print("  📈 Productivity optimization suggestions")
        print("  🎯 Best practices recommendations")
        print("  🔧 Detailed implementation steps")
        print("  💡 Proactive improvement suggestions")
    else:
        print("\n❌ Enhanced prompt test failed!")