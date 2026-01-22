import json
import os

HIGHSCORE_FILE = "highscores.json"

def load_scores():
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_scores(scores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(scores, f)

def add_score(name, score):
    scores = load_scores()
    scores.append({"name": name, "score": score})
    # Sort by score descending
    scores.sort(key=lambda x: x["score"], reverse=True)
    # Keep top 10
    scores = scores[:10]
    save_scores(scores)

def is_mid_high_score(score):
    """Check if the score qualifies for the top 10."""
    scores = load_scores()
    if len(scores) < 10:
        return True
    return score > scores[-1]["score"]

def get_top_scores():
    return load_scores()
