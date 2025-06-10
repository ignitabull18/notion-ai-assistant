#!/usr/bin/env python3
"""Check context limits and model configuration"""

import os
from dotenv import load_dotenv
from listeners.agno_integration import get_or_create_agent

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def check_context_limits():
    """Check the context limits and model configuration"""
    
    print("🔍 Checking AI agent context limits and configuration...")
    
    try:
        # Get agent
        agent = get_or_create_agent("context-check-session")
        print("✅ Agent created successfully")
        
        # Check model configuration
        if hasattr(agent, 'model'):
            model = agent.model
            print(f"\n🤖 Model Configuration:")
            print(f"  Model ID: {getattr(model, 'id', 'Unknown')}")
            print(f"  Model Type: {type(model)}")
            
            # Check for context/token limits
            context_attrs = [
                'max_tokens', 'context_length', 'context_window', 
                'max_context_length', 'token_limit', 'context_limit'
            ]
            
            for attr in context_attrs:
                if hasattr(model, attr):
                    value = getattr(model, attr)
                    print(f"  {attr}: {value}")
            
            # Check all model attributes
            print(f"\n📋 All Model Attributes:")
            for attr in sorted(dir(model)):
                if not attr.startswith('_') and not callable(getattr(model, attr, None)):
                    try:
                        value = getattr(model, attr)
                        if value is not None and str(value) != '':
                            print(f"  {attr}: {value}")
                    except:
                        pass
        
        # Check agent-level context settings
        if hasattr(agent, 'num_history_runs'):
            print(f"\n📚 Agent Context Settings:")
            print(f"  History runs: {agent.num_history_runs}")
            print(f"  Add history to messages: {getattr(agent, 'add_history_to_messages', 'Unknown')}")
            print(f"  Add memory references: {getattr(agent, 'add_memory_references', 'Unknown')}")
        
        # Check memory configuration
        if hasattr(agent, 'memory'):
            print(f"\n🧠 Memory Configuration:")
            print(f"  Memory type: {type(agent.memory)}")
            print(f"  Enable user memories: {getattr(agent, 'enable_user_memories', 'Unknown')}")
            print(f"  Enable session summaries: {getattr(agent, 'enable_session_summaries', 'Unknown')}")
        
        # Try to get model info from OpenAI (if using OpenAI)
        model_name = getattr(agent.model, 'id', 'unknown')
        if 'gpt' in model_name.lower() or 'o1' in model_name.lower() or 'o4' in model_name.lower():
            print(f"\n🔢 OpenAI Model '{model_name}' Expected Limits:")
            model_limits = {
                'gpt-4': '8K tokens (legacy)',
                'gpt-4-turbo': '128K tokens',
                'gpt-4o': '128K tokens', 
                'gpt-4o-mini': '128K tokens',
                'o1-preview': '128K tokens',
                'o1-mini': '128K tokens',
                'o4-mini': '128K tokens (estimated)'
            }
            
            for model_key, limit in model_limits.items():
                if model_key in model_name.lower():
                    print(f"  Expected context limit: {limit}")
                    break
            else:
                print(f"  Unknown model: {model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking context limits: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_context_limits()
    if success:
        print("\n🎉 Context limit check completed!")
    else:
        print("\n❌ Context limit check failed!")