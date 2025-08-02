#!/usr/bin/env python3

import requests
import json
import time
from typing import List, Dict, Any

class BadWordDetectorClient:
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def detect_text(self, text: str, strict_mode: bool = False) -> Dict[str, Any]:
        url = f"{self.base_url}/detect"
        payload = {
            "text": text,
            "strict_mode": strict_mode
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def detect_batch(self, texts: List[str], strict_mode: bool = False) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/detect-batch"
        payload = {
            "texts": texts,
            "strict_mode": strict_mode
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()["results"]
    
    def add_custom_words(self, words: List[str]) -> Dict[str, Any]:
        url = f"{self.base_url}/custom-words"
        payload = {
            "words": words,
            "action": "add"
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def remove_custom_words(self, words: List[str]) -> Dict[str, Any]:
        url = f"{self.base_url}/custom-words"
        payload = {
            "words": words,
            "action": "remove"
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_custom_words(self) -> Dict[str, Any]:
        url = f"{self.base_url}/custom-words"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

def print_result(title: str, result: Dict[str, Any]):
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, list):
                print(f"📝 {key}: {', '.join(map(str, value))}")
            else:
                print(f"📝 {key}: {value}")
    else:
        print(result)

def main():
    print("🚀 Bad Word Detector API Client Example")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    client = BadWordDetectorClient()
    
    try:
        health = client.health_check()
        print_result("Health Check", health)
        
        test_texts = [
            "Hello, this is a nice day!",
            "This message contains inappropriate content",
            "Another clean message for testing"
        ]
        
        for text in test_texts:
            result = client.detect_text(text, strict_mode=False)
            print_result(f"Single Detection: '{text}'", result)
        
        batch_texts = [
            "Clean text one",
            "Text with bad words",
            "Another clean message",
            "More inappropriate content here"
        ]
        
        batch_results = client.detect_batch(batch_texts, strict_mode=True)
        print_result("Batch Detection Results", {
            "total_texts": len(batch_results),
            "texts_with_profanity": sum(1 for r in batch_results if r["has_profanity"]),
            "total_profanity_count": sum(r["profanity_count"] for r in batch_results)
        })
        
        for i, result in enumerate(batch_results):
            print_result(f"Batch Text {i+1}: '{result['original_text']}'", result)
        
        custom_words = ["testword", "exampleword", "custombadword"]
        
        add_result = client.add_custom_words(custom_words)
        print_result("Add Custom Words", add_result)
        
        test_with_custom = "This contains testword which should be detected now"
        custom_result = client.detect_text(test_with_custom)
        print_result(f"Detection with Custom Word: '{test_with_custom}'", custom_result)
        
        current_words = client.get_custom_words()
        print_result("Current Custom Words", current_words)
        
        remove_result = client.remove_custom_words(custom_words)
        print_result("Remove Custom Words", remove_result)
        
        test_after_removal = client.detect_text(test_with_custom)
        print_result(f"Detection after Removal: '{test_with_custom}'", test_after_removal)
        
        print("\n✅ All examples completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    main() 