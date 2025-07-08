#!/usr/bin/env python3
"""
Debug script to test the question creation flow
This will help identify where the issue is occurring
"""

import sys
import os
from datetime import datetime
import uuid

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_question_creation_flow():
    """Simulate the question creation flow to find the issue"""
    print("🧪 Testing Question Creation Flow")
    print("=" * 50)
    
    # Simulate the state that would exist during question creation
    test_state = {
        "step": "ask_description",
        "subject": "Test Subject",
        "total": 1,  # Single question for testing
        "current": 0,  # First question (0-indexed)
        "duration_minutes": 15,
        "question": "What is 192.168.0.1?",
        "options": ["Local address", "Private address", "Public address", "None of them"],
        "correct_answer": "Private address",
        "batch": [],
        "batch_id": None
    }
    
    print("📋 Initial State:")
    for key, value in test_state.items():
        if key != "batch":  # Don't print empty batch
            print(f"   {key}: {value}")
    
    print("\n🔄 Simulating description step...")
    
    # Simulate receiving description
    description = "192.168.0.1 is a private IP address used in local networks."
    
    # Simulate the logic from TelegramBot.py
    try:
        batch_id = test_state.get("batch_id")
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
            test_state["batch_id"] = batch_id
            print(f"✅ Generated batch_id: {batch_id}")

        new_question = {
            "question": test_state["question"],
            "options": test_state["options"],
            "answer": test_state["correct_answer"],
            "description": description,
            "batch_id": batch_id,
            "subject": test_state["subject"]
        }
        
        print(f"✅ Created question object:")
        for key, value in new_question.items():
            print(f"   {key}: {value}")

        test_state["batch"].append(new_question)
        test_state["current"] += 1
        
        print(f"✅ Added to batch. Current: {test_state['current']}, Total: {test_state['total']}")

        # Check if this is the last question
        if test_state["current"] == test_state["total"]:
            print("🎯 This is the last question - should generate link now!")
            
            # Test link generation
            def generate_link_token():
                return str(uuid.uuid4())
            
            link_token = generate_link_token()
            print(f"✅ Generated link token: {link_token}")

            for q in test_state["batch"]:
                q["link_token"] = link_token
                q["used"] = False
            
            print(f"✅ Added token to {len(test_state['batch'])} questions")
            
            # Test database functions
            try:
                from db import save_question, save_batch_link
                
                print("🔄 Testing database save...")
                
                # Save questions (in test mode, we'll just print)
                for i, q in enumerate(test_state["batch"]):
                    print(f"   Question {i+1}: {q['question'][:30]}...")
                    # save_question(q)  # Uncomment to actually save
                
                duration = test_state.get("duration_minutes")
                print(f"🔄 Testing batch link save with duration: {duration}")
                
                # save_batch_link(batch_id, link_token, test_state["subject"], test_state["total"], duration)  # Uncomment to actually save
                
                unique_link = f"https://t.me/TestStudentCollegeBot?start=quiz_{link_token}"
                print(f"✅ Generated final link: {unique_link}")
                
                print("\n🎉 SUCCESS! Link generation flow completed successfully")
                
            except ImportError as e:
                print(f"❌ Database import error: {e}")
            except Exception as e:
                print(f"❌ Database error: {e}")
                
        else:
            print(f"📝 More questions needed. Moving to question {test_state['current'] + 1}")
            
    except Exception as e:
        print(f"❌ Error in flow: {e}")
        import traceback
        traceback.print_exc()

def test_imports():
    """Test if all required imports work"""
    print("\n🧪 Testing Imports")
    print("=" * 30)
    
    try:
        import uuid
        print("✅ uuid imported")
        
        from datetime import datetime
        print("✅ datetime imported")
        
        from db import save_question, save_batch_link
        print("✅ db functions imported")
        
        # Test uuid generation
        test_token = str(uuid.uuid4())
        print(f"✅ UUID generation works: {test_token[:8]}...")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")

def check_bot_state():
    """Check if there might be issues with bot state management"""
    print("\n🧪 Checking Bot State Management")
    print("=" * 40)
    
    # Simulate what happens when the bot receives a message
    print("📋 Simulating bot message handling...")
    
    # Check if the message handler would work
    test_chat_id = 12345
    test_message_text = "This is a test description for the answer."
    
    # Simulate insert_states
    insert_states = {
        test_chat_id: {
            "step": "ask_description",
            "subject": "Test Subject",
            "total": 1,
            "current": 0,
            "duration_minutes": 15,
            "question": "Test question?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "B",
            "batch": [],
            "batch_id": None
        }
    }
    
    print(f"✅ Simulated state for chat {test_chat_id}")
    
    # Check if state exists and step is correct
    if test_chat_id in insert_states:
        state = insert_states[test_chat_id]
        if state["step"] == "ask_description":
            print("✅ State exists and step is 'ask_description'")
            print("✅ Bot should process the description and generate link")
        else:
            print(f"❌ Wrong step: {state['step']}")
    else:
        print("❌ No state found for chat")

def main():
    """Main debug function"""
    print("🔍 DEBUG: Question Creation Flow")
    print("=" * 60)
    
    # Test imports first
    test_imports()
    
    # Test the question creation flow
    test_question_creation_flow()
    
    # Check bot state management
    check_bot_state()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUGGING COMPLETE")
    print("=" * 60)
    
    print("\n📋 If the flow works here but not in the bot:")
    print("   1. Check the bot logs for error messages")
    print("   2. Verify the bot is receiving the description message")
    print("   3. Check if the state is being preserved between messages")
    print("   4. Look for any exceptions in the bot console")
    
    print("\n💡 To debug the actual bot:")
    print("   1. The bot now has debug print statements")
    print("   2. Watch the console when creating a question")
    print("   3. You should see 'DEBUG:' messages showing the flow")
    print("   4. If no debug messages appear, the message isn't reaching the handler")

if __name__ == "__main__":
    main()
