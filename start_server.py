#!/usr/bin/env python3

import uvicorn
import os
import sys
from pathlib import Path

def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print("🚀 Starting Bad Word Detector API Server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print()
    print("📚 API Documentation will be available at:")
    print(f"   • Interactive docs: http://{host}:{port}/docs")
    print(f"   • ReDoc: http://{host}:{port}/redoc")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 