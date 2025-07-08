#!/usr/bin/env python3
"""
Simple 24/7 Bot Runner for Google Cloud Run
This is a simplified version that should work reliably on Google Cloud Run
"""

import os
import sys
import threading
import time
import requests
import signal
import subprocess
from datetime import datetime
from flask import Flask, jsonify

class Simple24x7Runner:
    def __init__(self):
        self.running = True
        self.start_time = datetime.now()
        self.last_ping = datetime.now()
        self.ping_count = 0
        self.port = int(os.environ.get('PORT', 8080))
        self.teacher_process = None
        self.student_process = None
        
        # Create Flask app
        self.create_flask_app()
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_flask_app(self):
        """Create Flask app with keep-alive endpoints"""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/')
        def home():
            return "🤖 Telegram Quiz Bot is running 24/7! 🎓"
        
        @self.flask_app.route('/health')
        def health():
            uptime = datetime.now() - self.start_time
            teacher_alive = self.teacher_process and self.teacher_process.poll() is None
            student_alive = self.student_process and self.student_process.poll() is None
            
            return jsonify({
                "status": "healthy" if teacher_alive and student_alive else "partial",
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_formatted": str(uptime),
                "teacher_bot_running": teacher_alive,
                "student_bot_running": student_alive,
                "last_ping": self.last_ping.isoformat(),
                "ping_count": self.ping_count,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.flask_app.route('/keep-alive')
        def keep_alive():
            self.last_ping = datetime.now()
            self.ping_count += 1
            
            return jsonify({
                "status": "alive",
                "message": "Bot is running 24/7",
                "ping_count": self.ping_count,
                "timestamp": self.last_ping.isoformat(),
                "uptime": str(datetime.now() - self.start_time)
            })
        
        @self.flask_app.route('/ping')
        def ping():
            return "pong"
        
        @self.flask_app.route('/restart')
        def restart_bots():
            """Emergency restart endpoint"""
            self.restart_all_bots()
            return jsonify({"status": "restarted", "timestamp": datetime.now().isoformat()})
    
    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_flask():
            try:
                self.log(f"🌐 Starting HTTP server on port {self.port}")
                self.flask_app.run(
                    host='0.0.0.0', 
                    port=self.port, 
                    debug=False, 
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                self.log(f"❌ Flask server error: {e}")
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)
        self.log("✅ HTTP server started successfully")
    
    def start_teacher_bot(self):
        """Start teacher bot as subprocess"""
        try:
            self.log("🎓 Starting Teacher Bot...")
            
            env = os.environ.copy()
            env['ENVIRONMENT'] = 'local'  # Force polling mode
            
            self.teacher_process = subprocess.Popen(
                [sys.executable, "TelegramBot.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            time.sleep(3)
            
            if self.teacher_process.poll() is None:
                self.log("✅ Teacher Bot started successfully")
                return True
            else:
                output, _ = self.teacher_process.communicate()
                self.log("❌ Teacher Bot failed to start")
                self.log(f"   Output: {output}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting Teacher Bot: {e}")
            return False
    
    def start_student_bot(self):
        """Start student bot as subprocess"""
        try:
            self.log("👨‍🎓 Starting Student Bot...")
            
            self.student_process = subprocess.Popen(
                [sys.executable, "StudentBot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            time.sleep(3)
            
            if self.student_process.poll() is None:
                self.log("✅ Student Bot started successfully")
                return True
            else:
                output, _ = self.student_process.communicate()
                self.log("❌ Student Bot failed to start")
                self.log(f"   Output: {output}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting Student Bot: {e}")
            return False
    
    def restart_all_bots(self):
        """Restart both bots"""
        self.log("🔄 Restarting all bots...")
        
        # Kill existing processes
        if self.teacher_process:
            try:
                self.teacher_process.terminate()
                self.teacher_process.wait(timeout=5)
            except:
                try:
                    self.teacher_process.kill()
                except:
                    pass
        
        if self.student_process:
            try:
                self.student_process.terminate()
                self.student_process.wait(timeout=5)
            except:
                try:
                    self.student_process.kill()
                except:
                    pass
        
        time.sleep(2)
        
        # Start fresh
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if teacher_ok and student_ok:
            self.log("✅ Both bots restarted successfully")
        else:
            self.log("❌ Failed to restart one or both bots")
    
    def self_ping_loop(self):
        """Self-ping to keep the service alive"""
        time.sleep(10)  # Wait for server to start
        
        while self.running:
            try:
                response = requests.get(
                    f"http://localhost:{self.port}/keep-alive",
                    timeout=10
                )
                if response.status_code == 200:
                    self.log(f"✅ Self-ping successful (total: {self.ping_count})")
                else:
                    self.log(f"⚠️ Self-ping returned status {response.status_code}")
            except Exception as e:
                self.log(f"❌ Self-ping failed: {e}")
            
            # Wait 5 minutes before next ping
            time.sleep(300)
    
    def monitor_bots_loop(self):
        """Monitor bot health and restart if needed"""
        while self.running:
            try:
                teacher_alive = self.teacher_process and self.teacher_process.poll() is None
                student_alive = self.student_process and self.student_process.poll() is None
                
                if not teacher_alive or not student_alive:
                    self.log("💀 One or both bots have died!")
                    self.log(f"Teacher Bot: {'✅ Running' if teacher_alive else '❌ Dead'}")
                    self.log(f"Student Bot: {'✅ Running' if student_alive else '❌ Dead'}")
                    
                    self.restart_all_bots()
                else:
                    uptime = datetime.now() - self.start_time
                    self.log(f"✅ Both bots healthy (uptime: {uptime})")
                
                # Check every 2 minutes
                time.sleep(120)
                
            except Exception as e:
                self.log(f"❌ Monitor error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the complete 24/7 system"""
        self.log("🚀 Starting Simple 24/7 Telegram Bot System")
        self.log("=" * 60)
        
        # Start HTTP server first
        self.start_flask_server()
        
        # Start both bots
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if teacher_ok and student_ok:
            self.log("🎉 System started successfully!")
            self.log("🎓 Teacher Bot: Running")
            self.log("👨‍🎓 Student Bot: Running")
            self.log(f"🌐 HTTP server: http://localhost:{self.port}")
            self.log("💬 Test by sending /start to your bots on Telegram")
        else:
            self.log("⚠️ Some bots failed to start")
        
        # Start self-ping in background
        ping_thread = threading.Thread(target=self.self_ping_loop, daemon=True)
        ping_thread.start()
        self.log("🔄 Self-ping system started (every 5 minutes)")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_bots_loop, daemon=True)
        monitor_thread.start()
        self.log("👀 Bot health monitoring started")
        
        return True
    
    def stop(self):
        """Stop all processes"""
        self.log("🛑 Stopping all processes...")
        self.running = False
        
        if self.teacher_process:
            self.teacher_process.terminate()
        if self.student_process:
            self.student_process.terminate()
        
        self.log("✅ All processes stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal")
    if 'runner' in globals():
        runner.stop()
    sys.exit(0)

def main():
    """Main function"""
    global runner
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    runner = Simple24x7Runner()
    
    try:
        if runner.start():
            # Keep main thread alive
            while True:
                time.sleep(60)
        else:
            print("❌ Failed to start the 24/7 system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        runner.stop()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        runner.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
