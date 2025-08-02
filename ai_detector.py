import re
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import gc

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: Transformers not available. Using fallback NLP methods.")

class AIDetector:
    def __init__(self):
        self.toxic_patterns = {
            "hate_speech": [
                r"\b(i\s+hate\s+you\b)",
                r"\b(i\s+despise\s+you\b)", 
                r"\b(you\s+are\s+stupid\b)",
                r"\b(you\s+are\s+dumb\b)",
                r"\b(you\s+are\s+an\s+idiot\b)",
                r"\b(you\s+suck\b)",
                r"\b(go\s+to\s+hell\b)",
                r"\b(fuck\s+you\b)",
                r"\b(fuck\s+off\b)",
                r"\b(piss\s+off\b)",
                r"\b(get\s+lost\b)",
                r"\b(you\s+are\s+worthless\b)",
                r"\b(you\s+are\s+useless\b)",
                r"\b(kill\s+yourself\b)",
                r"\b(you\s+should\s+die\b)",
                r"\b(i\s+hate\s+your\s+face\b)",
                r"\b(i\s+hate\s+your\s+guts\b)",
                r"\b(you\s+make\s+me\s+sick\b)",
                r"\b(you\s+disgust\s+me\b)",
                r"\b(you\s+are\s+disgusting\b)"
            ],
            "threats": [
                r"\b(i\s+will\s+kill\s+you\b)",
                r"\b(i\s+will\s+hurt\s+you\b)",
                r"\b(i\s+will\s+beat\s+you\b)",
                r"\b(i\s+will\s+punch\s+you\b)",
                r"\b(i\s+will\s+hit\s+you\b)",
                r"\b(you\s+will\s+pay\b)",
                r"\b(you\s+will\s+regret\b)",
                r"\b(i\s+swear\s+to\s+god\b)",
                r"\b(i\s+promise\s+you\s+will\s+pay\b)",
                r"\b(you\s+are\s+going\s+to\s+pay\b)"
            ],
            "insults": [
                r"\b(you\s+are\s+a\s+loser\b)",
                r"\b(you\s+are\s+a\s+failure\b)",
                r"\b(you\s+are\s+a\s+moron\b)",
                r"\b(you\s+are\s+a\s+retard\b)",
                r"\b(you\s+are\s+a\s+freak\b)",
                r"\b(you\s+are\s+a\s+weirdo\b)",
                r"\b(you\s+are\s+crazy\b)",
                r"\b(you\s+are\s+insane\b)",
                r"\b(you\s+are\s+mental\b)",
                r"\b(you\s+are\s+a\s+piece\s+of\s+shit\b)",
                r"\b(you\s+are\s+trash\b)",
                r"\b(you\s+are\s+garbage\b)"
            ],
            "discrimination": [
                r"\b(you\s+black\s+piece\s+of\s+shit\b)",
                r"\b(you\s+white\s+trash\b)",
                r"\b(you\s+chinese\s+dog\b)",
                r"\b(you\s+arab\s+terrorist\b)",
                r"\b(you\s+jew\s+bastard\b)",
                r"\b(you\s+muslim\s+fanatic\b)",
                r"\b(you\s+christian\s+zealot\b)",
                r"\b(you\s+gay\s+faggot\b)",
                r"\b(you\s+lesbian\s+dyke\b)",
                r"\b(you\s+trans\s+freak\b)"
            ]
        }
        
        self.toxic_words = {
            "profanity": {"fuck", "shit", "ass", "bitch", "bastard", "dick", "pussy", "cock", "whore", "slut", "fucker", "motherfucker", "bullshit", "fucking", "shitty", "asshole", "dumbass", "jackass", "damn", "hell", "crap"},
            "hate": {"hate", "despise", "loathe", "abhor", "detest"},
            "violence": {"kill", "murder", "beat", "punch", "hit", "hurt", "harm", "attack", "fight"},
            "insults": {"stupid", "dumb", "idiot", "moron", "retard", "loser", "failure", "worthless", "useless", "crazy", "insane", "mental", "freak", "weirdo"}
        }
        
        self.context_indicators = {
            "negative_emotions": ["angry", "mad", "furious", "rage", "hate", "despise", "loathe"],
            "threatening": ["kill", "hurt", "beat", "punch", "attack", "fight", "destroy"],
            "discriminatory": ["black", "white", "chinese", "arab", "jew", "muslim", "christian", "gay", "lesbian", "trans"],
            "intensifiers": ["very", "really", "extremely", "totally", "completely", "absolutely"]
        }
        
        self.sentiment_words = {
            "positive": {"love", "like", "good", "great", "awesome", "amazing", "wonderful", "beautiful", "nice", "kind", "sweet", "gentle", "caring", "helpful"},
            "negative": {"hate", "dislike", "bad", "terrible", "awful", "horrible", "ugly", "mean", "cruel", "rude", "aggressive", "violent"}
        }
        
        self.safe_contexts = {
            "activities": ["doing", "working", "studying", "reading", "writing", "cooking", "cleaning", "exercising", "running", "swimming", "dancing", "singing", "playing", "watching", "listening"],
            "objects": ["this", "that", "it", "them", "these", "those", "food", "music", "movie", "book", "game", "sport", "activity", "task", "job", "work"],
            "negations": ["don't", "do not", "doesn't", "does not", "didn't", "did not", "won't", "will not", "can't", "cannot", "not", "never", "no"]
        }
        
        self.toxic_phrases = [
            "i don't like you", "i dislike you", "i can't stand you", "you annoy me",
            "you bother me", "you irritate me", "you frustrate me", "you anger me",
            "you upset me", "you disappoint me", "you let me down", "you fail me",
            "you're not my type", "you're not for me", "you're not right for me",
            "you're not what i want", "you're not what i need", "you're not good enough",
            "you're not worth it", "you're not worth my time", "you're not worth my effort",
            "you are the worst", "you are terrible", "you are awful", "you are horrible",
            "you are disgusting", "you are repulsive", "you are vile", "you are despicable",
            "you are contemptible", "you are loathsome", "you are abhorrent", "you are detestable",
            "you are the worst person", "you are the worst human", "you are the worst thing",
            "you are the worst ever", "you are the worst of all", "you are the worst possible",
            "you are the worst imaginable", "you are the worst conceivable", "you are the worst thinkable"
        ]
        
        self.bypass_patterns = [
            r"\b(you\s+are\s+the\s+worst\b)",
            r"\b(you\s+are\s+terrible\b)",
            r"\b(you\s+are\s+awful\b)",
            r"\b(you\s+are\s+horrible\b)",
            r"\b(you\s+are\s+disgusting\b)",
            r"\b(you\s+are\s+repulsive\b)",
            r"\b(you\s+are\s+vile\b)",
            r"\b(you\s+are\s+despicable\b)",
            r"\b(you\s+are\s+contemptible\b)",
            r"\b(you\s+are\s+loathsome\b)",
            r"\b(you\s+are\s+abhorrent\b)",
            r"\b(you\s+are\s+detestable\b)",
            r"\b(you\s+mother\s*fuck\w*\b)",
            r"\b(you\s+father\s*fuck\w*\b)",
            r"\b(you\s+son\s*of\s*a\s*bitch\b)",
            r"\b(you\s+daughter\s*of\s*a\s*bitch\b)",
            r"\b(you\s+piece\s*of\s*shit\b)",
            r"\b(you\s+piece\s*of\s*garbage\b)",
            r"\b(you\s+piece\s*of\s*trash\b)",
            r"\b(you\s+piece\s*of\s*crap\b)",
            r"\b(you\s+piece\s*of\s*dirt\b)",
            r"\b(you\s+piece\s*of\s*scum\b)",
            r"\b(you\s+piece\s*of\s*filth\b)",
            r"\b(you\s+piece\s*of\s*garbage\b)",
            r"\b(you\s+piece\s*of\s*trash\b)",
            r"\b(you\s+piece\s*of\s*crap\b)",
            r"\b(you\s+piece\s*of\s*dirt\b)",
            r"\b(you\s+piece\s*of\s*scum\b)",
            r"\b(you\s+piece\s*of\s*filth\b)"
        ]
        
        self.toxicity_classifier = None
        self.sentiment_classifier = None
        self.sentiment_analyzer = TextBlob
        self.vectorizer = None
        self._toxic_vectors = None
        self._models_loaded = False
        
    def _load_ai_models(self):
        if self._models_loaded:
            return
            
        try:
            if TRANSFORMERS_AVAILABLE:
                print("Loading AI models...")
                self.toxicity_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    return_all_scores=True,
                    device=-1
                )
                self.sentiment_classifier = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=-1
                )
                print("AI models loaded successfully!")
            else:
                print("Transformers not available, using fallback methods")
            
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self._models_loaded = True
            
        except Exception as e:
            print(f"Error loading AI models: {e}")
            self.toxicity_classifier = None
            self.sentiment_classifier = None

    def analyze_sentence(self, text: str) -> Dict[str, Any]:
        if not self._models_loaded:
            self._load_ai_models()
            
        text_lower = text.lower().strip()
        text_normalized = self._normalize_text(text_lower)
        
        toxicity_score = 0.0
        detected_patterns = []
        detected_words = []
        context_score = 0.0
        sentiment_score = 0.0
        ai_toxicity_score = 0.0
        semantic_similarity_score = 0.0
        bypass_score = 0.0
        
        for category, patterns in self.toxic_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    detected_patterns.append({
                        "category": category,
                        "pattern": pattern,
                        "matches": matches
                    })
                    toxicity_score += 0.8
        
        for pattern in self.bypass_patterns:
            matches = re.findall(pattern, text_normalized, re.IGNORECASE)
            if matches:
                detected_patterns.append({
                    "category": "bypass_attempt",
                    "pattern": pattern,
                    "matches": matches
                })
                bypass_score += 0.9
        
        for category, words in self.toxic_words.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text_normalized):
                    if not self._is_safe_context(text_normalized, word):
                        detected_words.append({
                            "category": category,
                            "word": word
                        })
                        toxicity_score += 0.6
        
        context_score = self._analyze_context(text_normalized)
        sentiment_score = self._analyze_sentiment(text_normalized)
        
        if self.toxicity_classifier:
            ai_toxicity_score = self._analyze_with_ai(text)
        
        semantic_similarity_score = self._analyze_semantic_similarity(text_normalized)
        
        final_score = (toxicity_score + context_score + sentiment_score + ai_toxicity_score + semantic_similarity_score + bypass_score) / 6.0
        final_score = min(1.0, final_score)
        
        gc.collect()
        
        return {
            "toxicity_score": float(round(toxicity_score, 3)),
            "context_score": float(round(context_score, 3)),
            "sentiment_score": float(round(sentiment_score, 3)),
            "ai_toxicity_score": float(round(ai_toxicity_score, 3)),
            "semantic_similarity_score": float(round(semantic_similarity_score, 3)),
            "bypass_score": float(round(bypass_score, 3)),
            "final_score": float(round(final_score, 3)),
            "detected_patterns": detected_patterns,
            "detected_words": detected_words,
            "is_toxic": bool(final_score > 0.4),
            "severity": str(self._get_severity(final_score))
        }
    
    def _normalize_text(self, text: str) -> str:
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _analyze_with_ai(self, text: str) -> float:
        try:
            if self.toxicity_classifier:
                results = self.toxicity_classifier(text)
                toxic_score = 0.0
                for result in results[0]:
                    if result['label'] in ['toxic', 'hate', 'threat']:
                        toxic_score = max(toxic_score, result['score'])
                return float(toxic_score)
        except Exception as e:
            print(f"AI analysis error: {e}")
        return 0.0
    
    def _analyze_semantic_similarity(self, text: str) -> float:
        try:
            if self._toxic_vectors is None:
                self._toxic_vectors = self.vectorizer.fit_transform(self.toxic_phrases)
            
            text_vector = self.vectorizer.transform([text])
            similarities = cosine_similarity(text_vector, self._toxic_vectors)
            max_similarity = float(np.max(similarities))
            
            return max_similarity if max_similarity > 0.2 else 0.0
        except Exception as e:
            print(f"Semantic analysis error: {e}")
            return 0.0
    
    def _is_safe_context(self, text: str, word: str) -> bool:
        if word in ["hate", "dislike", "bad", "terrible", "awful"]:
            words = text.split()
            for i, w in enumerate(words):
                if w == word:
                    if i > 0 and words[i-1] in self.safe_contexts["negations"]:
                        return True
                    if i < len(words) - 1 and words[i+1] in self.safe_contexts["activities"]:
                        return True
                    if i < len(words) - 1 and words[i+1] in self.safe_contexts["objects"]:
                        return True
        return False
    
    def _analyze_context(self, text: str) -> float:
        score = 0.0
        
        for category, words in self.context_indicators.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    if not self._is_safe_context(text, word):
                        if category == "negative_emotions":
                            score += 0.3
                        elif category == "threatening":
                            score += 0.5
                        elif category == "discriminatory":
                            score += 0.7
                        elif category == "intensifiers":
                            score += 0.2
        
        return min(1.0, score)
    
    def _analyze_sentiment(self, text: str) -> float:
        try:
            blob = self.sentiment_analyzer(text)
            polarity = float(blob.sentiment.polarity)
            
            if polarity < -0.3:
                return abs(polarity)
            return 0.0
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.0
    
    def _get_severity(self, score: float) -> str:
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.3:
            return "low"
        else:
            return "none"
    
    def censor_text(self, text: str, analysis: Dict[str, Any]) -> str:
        censored_text = text
        
        for pattern_info in analysis["detected_patterns"]:
            for match in pattern_info["matches"]:
                pattern = re.compile(re.escape(match), re.IGNORECASE)
                censored_text = pattern.sub('*' * len(match), censored_text)
        
        for word_info in analysis["detected_words"]:
            word = word_info["word"]
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            censored_text = pattern.sub('*' * len(word), censored_text)
        
        return censored_text 