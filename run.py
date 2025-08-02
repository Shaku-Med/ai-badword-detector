#!/usr/bin/env python3

import os
import sys
import subprocess

def main():
    print("🚀 Bad Word Detector API")
    print("=" * 30)
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment")
        print("💡 Consider running: python setup.py")
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        return 1
    
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install dependencies with: pip install -r requirements.txt")
        return 1
    
    print("\n🌐 Starting server on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 