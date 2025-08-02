from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
import json
import os
from ai_detector import AIDetector

app = FastAPI(
    title="Bad Word Detector API",
    description="A FastAPI-based API for detecting and filtering inappropriate content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str
    language: str = "en"
    strict_mode: bool = False

class TextResponse(BaseModel):
    original_text: str
    has_profanity: bool
    profanity_count: int
    profanity_words: List[str]
    censored_text: str
    confidence_score: float
    ai_analysis: Optional[Dict[str, Any]] = None

class BatchTextRequest(BaseModel):
    texts: List[str]
    language: str = "en"
    strict_mode: bool = False

class BatchTextResponse(BaseModel):
    results: List[TextResponse]

class CustomWordRequest(BaseModel):
    words: List[str]
    action: str = "add"

class CustomWordResponse(BaseModel):
    message: str
    current_custom_words: List[str]

DEFAULT_BAD_WORDS = {
    "bad", "damn", "hell", "crap", "shit", "fuck", "ass", "bitch", "bastard", 
    "dick", "pussy", "cock", "whore", "slut", "fucker", "motherfucker",
    "bullshit", "fucking", "shitty", "asshole", "dumbass", "jackass"
}

CUSTOM_BAD_WORDS = set()
ai_detector = AIDetector()

def load_custom_words():
    try:
        if os.path.exists("custom_bad_words.json"):
            with open("custom_bad_words.json", "r") as f:
                data = json.load(f)
                CUSTOM_BAD_WORDS.update(data.get("words", []))
    except Exception as e:
        print(f"Error loading custom words: {e}")

def save_custom_words():
    try:
        with open("custom_bad_words.json", "w") as f:
            json.dump({"words": list(CUSTOM_BAD_WORDS)}, f)
    except Exception as e:
        print(f"Error saving custom words: {e}")

def detect_profanity(text: str, strict_mode: bool = False) -> Dict[str, Any]:
    all_bad_words = DEFAULT_BAD_WORDS.union(CUSTOM_BAD_WORDS)
    
    text_lower = text.lower()
    
    profanity_words = []
    for word in all_bad_words:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            profanity_words.append(word)
    
    profanity_count = len(profanity_words)
    has_profanity = profanity_count > 0
    
    censored_text = text
    for word in profanity_words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        censored_text = pattern.sub('*' * len(word), censored_text)
    
    word_count = len(text.split())
    confidence_score = min(1.0, profanity_count / max(word_count, 1))
    
    if strict_mode and has_profanity:
        confidence_score = min(confidence_score + 0.2, 1.0)
    
    ai_analysis = ai_detector.analyze_sentence(text)
    
    if ai_analysis["is_toxic"] or ai_analysis["ai_toxicity_score"] > 0.6:
        has_profanity = True
        confidence_score = max(confidence_score, ai_analysis["final_score"])
        censored_text = ai_detector.censor_text(text, ai_analysis)
    
    return {
        "has_profanity": has_profanity,
        "profanity_count": profanity_count,
        "profanity_words": profanity_words,
        "censored_text": censored_text,
        "confidence_score": round(confidence_score, 3),
        "ai_analysis": ai_analysis
    }

@app.on_event("startup")
async def startup_event():
    load_custom_words()

@app.get("/")
async def root():
    return {
        "message": "Bad Word Detector API",
        "version": "1.0.0",
        "endpoints": {
            "/detect": "POST - Detect profanity in single text",
            "/detect-get": "GET - Detect profanity with query parameters",
            "/detect-batch": "Detect profanity in multiple texts",
            "/custom-words": "Manage custom bad words",
            "/health": "Health check endpoint"
        }
    }

@app.get("/detect-get", response_model=TextResponse)
async def detect_bad_words_get(
    word: str = Query(..., description="Text to check for profanity"),
    strict_mode: bool = Query(False, description="Enable strict mode for enhanced detection")
):
    try:
        result = detect_profanity(word, strict_mode)
        
        return TextResponse(
            original_text=word,
            has_profanity=result["has_profanity"],
            profanity_count=result["profanity_count"],
            profanity_words=result["profanity_words"],
            censored_text=result["censored_text"],
            confidence_score=result["confidence_score"],
            ai_analysis=result["ai_analysis"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/detect", response_model=TextResponse)
async def detect_bad_words(request: TextRequest):
    try:
        result = detect_profanity(request.text, request.strict_mode)
        
        return TextResponse(
            original_text=request.text,
            has_profanity=result["has_profanity"],
            profanity_count=result["profanity_count"],
            profanity_words=result["profanity_words"],
            censored_text=result["censored_text"],
            confidence_score=result["confidence_score"],
            ai_analysis=result["ai_analysis"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/detect-batch", response_model=BatchTextResponse)
async def detect_bad_words_batch(request: BatchTextRequest):
    try:
        results = []
        for text in request.texts:
            result = detect_profanity(text, request.strict_mode)
            results.append(TextResponse(
                original_text=text,
                has_profanity=result["has_profanity"],
                profanity_count=result["profanity_count"],
                profanity_words=result["profanity_words"],
                censored_text=result["censored_text"],
                confidence_score=result["confidence_score"],
                ai_analysis=result["ai_analysis"]
            ))
        
        return BatchTextResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.post("/custom-words", response_model=CustomWordResponse)
async def manage_custom_words(request: CustomWordRequest):
    try:
        if request.action == "add":
            CUSTOM_BAD_WORDS.update(request.words)
            message = f"Added {len(request.words)} custom words"
        elif request.action == "remove":
            CUSTOM_BAD_WORDS.difference_update(request.words)
            message = f"Removed {len(request.words)} custom words"
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'")
        
        save_custom_words()
        
        return CustomWordResponse(
            message=message,
            current_custom_words=list(CUSTOM_BAD_WORDS)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing custom words: {str(e)}")

@app.get("/custom-words")
async def get_custom_words():
    return {
        "custom_words": list(CUSTOM_BAD_WORDS),
        "count": len(CUSTOM_BAD_WORDS)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "custom_words_count": len(CUSTOM_BAD_WORDS),
        "profanity_filter_loaded": True,
        "ai_detector_loaded": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 