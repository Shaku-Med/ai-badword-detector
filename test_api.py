import requests
import json

BASE_URL = "http://localhost:8000"

def test_single_detection():
    print("=== Testing Single Text Detection ===")
    
    clean_text = "Hello, this is a nice day!"
    response = requests.post(f"{BASE_URL}/detect", json={
        "text": clean_text,
        "strict_mode": False
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Clean text: {clean_text}")
        print(f"Has profanity: {result['has_profanity']}")
        print(f"Profanity count: {result['profanity_count']}")
        print(f"Confidence score: {result['confidence_score']}")
        print(f"Censored text: {result['censored_text']}")
        print()
    
    profane_text = "This is a bad word example"
    response = requests.post(f"{BASE_URL}/detect", json={
        "text": profane_text,
        "strict_mode": True
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Text with profanity: {profane_text}")
        print(f"Has profanity: {result['has_profanity']}")
        print(f"Profanity words: {result['profanity_words']}")
        print(f"Profanity count: {result['profanity_count']}")
        print(f"Confidence score: {result['confidence_score']}")
        print(f"Censored text: {result['censored_text']}")
        print()

def test_batch_detection():
    print("=== Testing Batch Text Detection ===")
    
    texts = [
        "Hello, how are you?",
        "This is a nice day!",
        "Some inappropriate content here",
        "Another clean message"
    ]
    
    response = requests.post(f"{BASE_URL}/detect-batch", json={
        "texts": texts,
        "strict_mode": False
    })
    
    if response.status_code == 200:
        results = response.json()["results"]
        for i, result in enumerate(results):
            print(f"Text {i+1}: {result['original_text']}")
            print(f"  Has profanity: {result['has_profanity']}")
            print(f"  Profanity count: {result['profanity_count']}")
            print(f"  Profanity words: {result['profanity_words']}")
            print()

def test_custom_words():
    print("=== Testing Custom Words Management ===")
    
    custom_words = ["testword", "exampleword"]
    response = requests.post(f"{BASE_URL}/custom-words", json={
        "words": custom_words,
        "action": "add"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        print(f"Current custom words: {result['current_custom_words']}")
        print()
    
    test_text = "This contains testword which should be detected"
    response = requests.post(f"{BASE_URL}/detect", json={
        "text": test_text,
        "strict_mode": False
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Text with custom word: {test_text}")
        print(f"Has profanity: {result['has_profanity']}")
        print(f"Profanity words: {result['profanity_words']}")
        print(f"Censored text: {result['censored_text']}")
        print()
    
    response = requests.post(f"{BASE_URL}/custom-words", json={
        "words": custom_words,
        "action": "remove"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        print(f"Current custom words: {result['current_custom_words']}")
        print()

def test_health_check():
    print("=== Testing Health Check ===")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Custom words count: {result['custom_words_count']}")
        print(f"Profanity filter loaded: {result['profanity_filter_loaded']}")
        print()

def test_api_info():
    print("=== Testing API Information ===")
    
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        print(f"Version: {result['version']}")
        print("Available endpoints:")
        for endpoint, description in result['endpoints'].items():
            print(f"  {endpoint}: {description}")
        print()

if __name__ == "__main__":
    try:
        test_api_info()
        test_health_check()
        test_single_detection()
        test_batch_detection()
        test_custom_words()
        
        print("All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
        print("To start the server, run: python main.py")
    except Exception as e:
        print(f"Error during testing: {e}") 