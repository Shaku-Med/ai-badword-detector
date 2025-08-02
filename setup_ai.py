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
    print("🤖 Setting up AI Bad Word Detector...")
    print("=" * 50)
    
    if os.name == 'nt':
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    ai_packages = [
        "transformers",
        "torch",
        "numpy",
        "scikit-learn",
        "nltk",
        "textblob"
    ]
    
    for package in ai_packages:
        if not run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    print("\n📥 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        print("✅ NLTK data downloaded successfully")
    except Exception as e:
        print(f"⚠️  NLTK download failed: {e}")
    
    print("\n🤖 Testing AI models...")
    try:
        from ai_detector import AIDetector
        detector = AIDetector()
        test_result = detector.analyze_sentence("I don't like you")
        print(f"✅ AI detector test successful: {test_result['final_score']}")
    except Exception as e:
        print(f"⚠️  AI detector test failed: {e}")
    
    print("\n✅ AI setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the server: python main.py")
    print("2. Test with: http://localhost:8000/detect-get?word=I%20don't%20like%20you")
    print("\n🤖 AI Features:")
    print("- Transformers-based toxicity detection")
    print("- Semantic similarity analysis")
    print("- Advanced sentiment analysis")
    print("- Context-aware understanding")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 