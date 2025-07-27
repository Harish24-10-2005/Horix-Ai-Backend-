#!/usr/bin/env python3
"""
Enhanced AI Agent Protocol - Environment Setup Script
Automates the setup of virtual environment and dependencies using uv
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📋 {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("⚠️  Please install Python 3.8 or higher from https://python.org")
        return False

def install_uv():
    """Install uv package manager"""
    print("🔍 Checking if uv is installed...")
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing uv...")
        return run_command("pip install uv", "uv installation")

def setup_virtual_environment():
    """Create virtual environment with uv"""
    if os.path.exists(".venv"):
        print("✅ Virtual environment already exists")
        return True
    return run_command("uv venv", "Virtual environment creation")

def install_dependencies():
    """Install dependencies using uv"""
    if platform.system() == "Windows":
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = "uv pip install -r requirements.txt"
        full_cmd = f"{activate_cmd} && {pip_cmd}"
    else:
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = "uv pip install -r requirements.txt"
        full_cmd = f"{activate_cmd} && {pip_cmd}"
    
    return run_command(full_cmd, "Dependencies installation")

def verify_installation():
    """Verify the installation by running status check"""
    if platform.system() == "Windows":
        cmd = ".venv\\Scripts\\activate && python status_check.py"
    else:
        cmd = "source .venv/bin/activate && python status_check.py"
    
    return run_command(cmd, "Installation verification")

def main():
    """Main setup function"""
    print("🚀 Enhanced AI Agent Protocol - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install uv
    if not install_uv():
        print("❌ Failed to install uv. Please install manually:")
        print("   pip install uv")
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Verify installation
    print("\n🧪 Verifying installation...")
    if verify_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        if platform.system() == "Windows":
            print("1. Activate virtual environment: .venv\\Scripts\\activate")
        else:
            print("1. Activate virtual environment: source .venv/bin/activate")
        print("2. Run the system: python final_demo.py")
        print("3. Choose Option 1 for Comprehensive Demo")
    else:
        print("\n⚠️  Setup completed but verification failed")
        print("   You can still try running: python final_demo.py")

if __name__ == "__main__":
    main()
