#!/usr/bin/env python3
"""
Quick fix script to restore the original question flow if needed
This provides both the new flow (with descriptions) and original flow (without descriptions)
"""

def show_original_flow():
    """Show the original working flow without descriptions"""
    print("📋 ORIGINAL FLOW (without descriptions):")
    print("""
    elif state["step"] == "ask_answer":
        if not message.text.isdigit():
            choices_count = state.get("choices_count", 4)
            bot.send_message(chat_id, f"❗ الرجاء إرسال رقم صحيح من 1 إلى {choices_count}.")
            return
        answer_index = int(message.text) - 1
        choices_count = state.get("choices_count", 4)
        if answer_index not in range(choices_count):
            bot.send_message(chat_id, f"❗ الرقم خارج النطاق، الرجاء إرسال رقم بين 1 و{choices_count}.")
            return

        correct_text = state["options"][answer_index]
        batch_id = state.get("batch_id")
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
            state["batch_id"] = batch_id

        new_question = {
            "question": state["question"],
            "options": state["options"],
            "answer": correct_text,
            "batch_id": batch_id,
            "subject": state["subject"]
        }

        state["batch"].append(new_question)
        state["current"] += 1

        if state["current"] == state["total"]:
            # توليد رمز فريد للربط
            link_token = generate_link_token()

            for q in state["batch"]:
                q["link_token"] = link_token
                q["used"] = False

            for q in state["batch"]:
                save_question(q)

            duration = state.get("duration_minutes")

            save_batch_link(batch_id, link_token, state["subject"], state["total"], duration)

            unique_link = f"https://t.me/TestStudentCollegeBot?start=quiz_{link_token}"
            bot.send_message(chat_id,
                f"✅ تم إدخال {state['total']} سؤال بنجاح.\\n"
                f"مدة الاختبار: {duration} دقيقة\\n"
                f"هذا هو رابط الاختبار الخاص (خاص بشخص واحد فقط):\\n{unique_link}\\n\\n"
                f"يرجى إرسال هذا الرابط للطالب المخصص فقط.")
            insert_states.pop(chat_id)
        else:
            state["step"] = "ask_question"
            bot.send_message(chat_id, f"📝 أرسل نص السؤال رقم {state['current'] + 1}:")
    """)

def show_new_flow():
    """Show the new flow with descriptions"""
    print("📋 NEW FLOW (with descriptions):")
    print("""
    elif state["step"] == "ask_answer":
        # ... same validation code ...
        correct_text = state["options"][answer_index]
        state["correct_answer"] = correct_text
        state["step"] = "ask_description"
        
        bot.send_message(chat_id,
            f"✅ الإجابة الصحيحة: {correct_text}\\n\\n"
            f"📝 الآن أرسل وصف أو تفسير لماذا هذه الإجابة صحيحة:")

    elif state["step"] == "ask_description":
        description = message.text
        # ... create question with description ...
        # ... same link generation logic ...
    """)

def create_hybrid_solution():
    """Create a solution that allows both with and without descriptions"""
    print("🔧 HYBRID SOLUTION:")
    print("You can modify the bot to ask if you want to add a description:")
    print("""
    elif state["step"] == "ask_answer":
        # ... validation code ...
        correct_text = state["options"][answer_index]
        state["correct_answer"] = correct_text
        
        # Ask if user wants to add description
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📝 إضافة وصف", callback_data="add_description"),
            types.InlineKeyboardButton("⏭️ تخطي", callback_data="skip_description")
        )
        
        bot.send_message(chat_id,
            f"✅ الإجابة الصحيحة: {correct_text}\\n\\n"
            f"هل تريد إضافة وصف لهذه الإجابة؟",
            reply_markup=markup)
    """)

def troubleshooting_steps():
    """Provide troubleshooting steps"""
    print("\n🔍 TROUBLESHOOTING STEPS:")
    print("=" * 50)
    
    print("1. 📊 Check Bot Logs:")
    print("   - Look for 'DEBUG:' messages in the console")
    print("   - Check for any error messages")
    print("   - Verify the bot receives the description message")
    
    print("\n2. 🧪 Test the Debug Script:")
    print("   - Run: python debug_question_flow.py")
    print("   - This will test the logic without the bot")
    
    print("\n3. 📝 Manual Test:")
    print("   - Start question creation: /insertQuestions")
    print("   - Go through all steps until description")
    print("   - Send a simple description like 'test'")
    print("   - Watch console for debug messages")
    
    print("\n4. 🔄 Quick Fix Options:")
    print("   a) Temporarily disable descriptions (use original flow)")
    print("   b) Make descriptions optional")
    print("   c) Add more error handling")
    
    print("\n5. 🐛 Common Issues:")
    print("   - State not preserved between messages")
    print("   - Exception in database save")
    print("   - Message handler not triggered")
    print("   - Import errors")

def quick_fix_code():
    """Provide quick fix code"""
    print("\n🚀 QUICK FIX CODE:")
    print("=" * 30)
    print("If you want to temporarily disable descriptions, replace the ask_answer section with:")
    print("""
    elif state["step"] == "ask_answer":
        if not message.text.isdigit():
            choices_count = state.get("choices_count", 4)
            bot.send_message(chat_id, f"❗ الرجاء إرسال رقم صحيح من 1 إلى {choices_count}.")
            return
        answer_index = int(message.text) - 1
        choices_count = state.get("choices_count", 4)
        if answer_index not in range(choices_count):
            bot.send_message(chat_id, f"❗ الرقم خارج النطاق، الرجاء إرسال رقم بين 1 و{choices_count}.")
            return

        correct_text = state["options"][answer_index]
        batch_id = state.get("batch_id")
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
            state["batch_id"] = batch_id

        new_question = {
            "question": state["question"],
            "options": state["options"],
            "answer": correct_text,
            "description": "",  # Empty description for now
            "batch_id": batch_id,
            "subject": state["subject"]
        }

        state["batch"].append(new_question)
        state["current"] += 1

        if state["current"] == state["total"]:
            try:
                link_token = generate_link_token()
                for q in state["batch"]:
                    q["link_token"] = link_token
                    q["used"] = False
                for q in state["batch"]:
                    save_question(q)
                duration = state.get("duration_minutes")
                save_batch_link(batch_id, link_token, state["subject"], state["total"], duration)
                unique_link = f"https://t.me/TestStudentCollegeBot?start=quiz_{link_token}"
                bot.send_message(chat_id,
                    f"✅ تم إدخال {state['total']} سؤال بنجاح.\\n"
                    f"مدة الاختبار: {duration} دقيقة\\n"
                    f"⏰ صالح لمدة ساعتين من الآن\\n"
                    f"هذا هو رابط الاختبار الخاص:\\n{unique_link}")
                insert_states.pop(chat_id)
            except Exception as e:
                bot.send_message(chat_id, f"❌ خطأ في إنشاء الرابط: {str(e)}")
        else:
            state["step"] = "ask_question"
            bot.send_message(chat_id, f"📝 أرسل نص السؤال رقم {state['current'] + 1}:")
    """)

def main():
    """Main function"""
    print("🔧 Question Flow Fix Helper")
    print("=" * 60)
    
    show_original_flow()
    print("\n" + "="*60)
    show_new_flow()
    print("\n" + "="*60)
    create_hybrid_solution()
    print("\n" + "="*60)
    troubleshooting_steps()
    print("\n" + "="*60)
    quick_fix_code()
    
    print("\n🎯 RECOMMENDATION:")
    print("1. First run: python debug_question_flow.py")
    print("2. Check bot console for DEBUG messages")
    print("3. If still not working, use the quick fix code above")
    print("4. Once working, we can add descriptions back gradually")

if __name__ == "__main__":
    main()
