from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Travel Recommendation API")

# Allow all origins (you can restrict to your frontend later)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, etc.
    allow_headers=["*"],         # Allow all headers
)

# Request model
class UserPreference(BaseModel):
    budget: str
    vibe: List[str]
    min_accommodation_rating: int
    min_safety_rating: int
    preferred_crowd: str
    liked: List[str]
    disliked: List[str]

# Sample data
PLACES = [
    {
        "name": "Eiffel Tower",
        "budget": "medium",
        "vibe": ["romantic", "historic"],
        "accommodation_rating": 4,
        "safety_rating": 5,
        "crowd_level": "high",
        "tags": ["city", "historic", "romantic"]
    },
    {
        "name": "Colosseum",
        "budget": "medium",
        "vibe": ["historic"],
        "accommodation_rating": 4,
        "safety_rating": 4,
        "crowd_level": "high",
        "tags": ["historic", "ancient", "city"]
    },
    {
        "name": "Maldives Beach",
        "budget": "high",
        "vibe": ["relaxing", "romantic"],
        "accommodation_rating": 5,
        "safety_rating": 5,
        "crowd_level": "low",
        "tags": ["beach", "island", "luxury"]
    },
    {
        "name": "Bondi Beach",
        "budget": "low",
        "vibe": ["adventure", "fun"],
        "accommodation_rating": 3,
        "safety_rating": 4,
        "crowd_level": "high",
        "tags": ["beach", "surfing", "sun"]
    }
]

# Healthcheck endpoint
@app.get("/health", summary="Check if the API is running")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}

# Recommendation endpoint
@app.post("/recommend", summary="Get top 3 recommended places based on user preferences")
def recommend_places(preference: UserPreference) -> Dict[str, List[Dict]]:
    recommendations = []

    for place in PLACES:
        score = 0

        # budget match
        if place["budget"] == preference.budget:
            score += 1

        # vibe match
        score += len(set(place["vibe"]) & set(preference.vibe)) * 2

        # liked tags
        score += len(set(place["tags"]) & set(preference.liked))

        # disliked tags
        score -= len(set(place["tags"]) & set(preference.disliked)) * 2

        # rating filters
        if place["accommodation_rating"] < preference.min_accommodation_rating:
            continue
        if place["safety_rating"] < preference.min_safety_rating:
            continue

        # crowd preference
        if place["crowd_level"] == preference.preferred_crowd:
            score += 1

        if score > 0:
            recommendations.append({
                "place": place["name"],
                "score": score
            })

    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return {
        "recommended_places": recommendations[:3]
    }
