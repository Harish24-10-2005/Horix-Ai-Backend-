#!/usr/bin/env python3
"""
MCP AI Configuration Setup
==========================
Installs dependencies needed for AI-powered MCP configuration
"""

import subprocess
import sys
import os

def install_ai_dependencies():
    """Install LangChain and Groq dependencies for AI configuration"""
    print("🤖 Installing AI configuration dependencies...")
    
    packages = [
        "langchain-groq",
        "langchain",
        "langchain-core"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All AI dependencies installed successfully!")
    print("\n🔑 To enable AI configuration, set your GROQ API key:")
    print("   export GROQ_API_KEY='your_groq_api_key_here'")
    print("   # or add it to your .env file")
    print("\n🚀 You can get a free Groq API key at: https://console.groq.com/")
    return True

def check_ai_setup():
    """Check if AI configuration is properly set up"""
    try:
        import langchain_groq
        import langchain
        groq_key = os.getenv('GROQ_API_KEY')
        
        if groq_key:
            print("✅ AI configuration fully enabled!")
            return True
        else:
            print("⚠️  AI dependencies installed but GROQ_API_KEY not set")
            print("   Set GROQ_API_KEY environment variable to enable AI features")
            return False
    except ImportError:
        print("❌ AI dependencies not installed")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_ai_setup()
    else:
        install_ai_dependencies()
