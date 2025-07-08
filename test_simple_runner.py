#!/usr/bin/env python3
"""
Test the simple 24/7 runner
"""

import os
import sys
import time
import requests
import threading
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_endpoints():
    """Test all HTTP endpoints"""
    log("🧪 Testing HTTP endpoints...")
    
    base_url = "http://localhost:8080"
    endpoints = [
        ("/", "Home page"),
        ("/health", "Health check"),
        ("/keep-alive", "Keep-alive"),
        ("/ping", "Ping test")
    ]
    
    # Wait for server to start
    time.sleep(15)
    
    all_good = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=15)
            if response.status_code == 200:
                log(f"✅ {description}: OK")
                
                # Show details for health endpoint
                if endpoint == "/health":
                    try:
                        data = response.json()
                        log(f"   Teacher Bot: {'✅ Running' if data.get('teacher_bot_running') else '❌ Not running'}")
                        log(f"   Student Bot: {'✅ Running' if data.get('student_bot_running') else '❌ Not running'}")
                        log(f"   Uptime: {data.get('uptime_formatted', 'unknown')}")
                        log(f"   Status: {data.get('status', 'unknown')}")
                    except Exception as e:
                        log(f"   Could not parse JSON: {e}")
                        
                elif endpoint == "/keep-alive":
                    try:
                        data = response.json()
                        log(f"   Ping count: {data.get('ping_count', 'unknown')}")
                    except Exception as e:
                        log(f"   Could not parse JSON: {e}")
                        
            else:
                log(f"❌ {description}: Status {response.status_code}")
                all_good = False
                
        except requests.exceptions.ConnectionError:
            log(f"❌ {description}: Connection failed (server not ready?)")
            all_good = False
        except Exception as e:
            log(f"❌ {description}: Error - {e}")
            all_good = False
    
    return all_good

def monitor_system():
    """Monitor the system for a while"""
    log("👀 Monitoring system for 3 minutes...")
    
    base_url = "http://localhost:8080"
    
    for i in range(6):  # Check 6 times over 3 minutes
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                teacher_running = data.get('teacher_bot_running', False)
                student_running = data.get('student_bot_running', False)
                uptime = data.get('uptime_formatted', 'unknown')
                
                status = "✅ Healthy" if teacher_running and student_running else "⚠️ Partial"
                log(f"{status} - Teacher: {'✅' if teacher_running else '❌'}, Student: {'✅' if student_running else '❌'}, Uptime: {uptime}")
                
                # If both bots are running, we can test them
                if teacher_running and student_running:
                    log("🎉 Both bots are running! You can test them on Telegram now.")
                    break
            else:
                log(f"❌ Health check failed with status {response.status_code}")
        except Exception as e:
            log(f"❌ Health check error: {e}")
        
        if i < 5:  # Don't wait after last check
            time.sleep(30)  # Wait 30 seconds between checks

def main():
    """Main test function"""
    log("🧪 Testing Simple 24/7 Bot Runner")
    log("=" * 60)
    log("This will test the simple subprocess-based bot runner")
    log("that should work reliably on Google Cloud Run.")
    log("=" * 60)
    
    # Check if required files exist
    required_files = ["TelegramBot.py", "StudentBot.py", "simple_24x7_runner.py"]
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            log(f"✅ {file}")
        else:
            log(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        log("❌ Missing required files. Please ensure all files are present.")
        return
    
    # Set environment for testing
    os.environ['PORT'] = '8080'
    
    try:
        log("🚀 Starting simple bot runner...")
        
        # Start the system in a separate thread
        def run_system():
            try:
                from simple_24x7_runner import Simple24x7Runner
                runner = Simple24x7Runner()
                runner.start()
                
                # Keep it running
                while True:
                    time.sleep(1)
            except Exception as e:
                log(f"❌ System error: {e}")
                import traceback
                traceback.print_exc()
        
        # Start system in background
        system_thread = threading.Thread(target=run_system, daemon=True)
        system_thread.start()
        
        # Test endpoints
        if test_endpoints():
            log("✅ All endpoints working!")
        else:
            log("⚠️ Some endpoints failed")
        
        # Monitor the system
        monitor_system()
        
        # Final status check
        log("🏥 Final status check...")
        try:
            response = requests.get("http://localhost:8080/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                teacher_running = data.get('teacher_bot_running', False)
                student_running = data.get('student_bot_running', False)
                
                log("📊 Final Results:")
                log(f"   HTTP Server: ✅ Running")
                log(f"   Teacher Bot: {'✅ Running' if teacher_running else '❌ Not running'}")
                log(f"   Student Bot: {'✅ Running' if student_running else '❌ Not running'}")
                log(f"   System Status: {'✅ Fully Operational' if teacher_running and student_running else '⚠️ Partial Operation'}")
                
                if teacher_running and student_running:
                    log("🎉 SUCCESS! Both bots are running!")
                    log("💬 Test your bots on Telegram:")
                    log("   1. Send /start to your Teacher Bot")
                    log("   2. Send /start to @TestStudentCollegeBot")
                    log("   3. Create a quiz and test the full flow")
                else:
                    log("⚠️ Some bots are not running. Common issues:")
                    log("   - Bot tokens not configured correctly")
                    log("   - Network connectivity issues")
                    log("   - Database connection problems")
                    log("   - pyTelegramBotAPI version conflicts")
        except Exception as e:
            log(f"❌ Final status check failed: {e}")
        
        log("=" * 60)
        log("✅ Test completed!")
        log("📋 Next steps:")
        log("   1. If bots are running locally, deploy to Google Cloud Run")
        log("   2. Use Dockerfile.simple for deployment")
        log("   3. Set up external monitoring with UptimeRobot")
        
    except KeyboardInterrupt:
        log("\n🛑 Test stopped by user")
    except Exception as e:
        log(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
