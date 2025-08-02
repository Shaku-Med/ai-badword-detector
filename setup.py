#!/usr/bin/env python3

import subprocess
import sys
import os

def run_command(command, description):
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Bad Word Detector API...")
    print("=" * 50)
    
    if not run_command("python3 --version", "Checking Python 3"):
        print("❌ Python 3 is not available. Please install Python 3 first.")
        return False
    
    if os.path.exists("venv"):
        print("📁 Virtual environment already exists")
    else:
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            print("❌ Failed to create virtual environment")
            print("💡 Try installing python3-venv:")
            print("   sudo apt install python3-venv")
            return False
    
    if os.name == 'nt':
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        print("⚠️  Failed to upgrade pip, continuing anyway...")
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return False
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the server:")
    print("   python main.py")
    print("3. Or use the startup script:")
    print("   python start_server.py")
    print("\n🌐 The API will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 