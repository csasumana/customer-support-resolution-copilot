from typing import Dict, List, Tuple
import numpy as np
from app.retrieval.embedder import embed_text


# IMPORTANT:
# Only "issue classes" go here.
# Do NOT include requested remedies like refund_request.
INTENT_EXEMPLARS: Dict[str, List[str]] = {
    "delivery_delay": [
        "My order arrived very late",
        "The delivery was delayed by a long time",
        "My food came much later than promised",
        "The order took too long to arrive",
    ],
    "missing_item": [
        "One item was missing from my order",
        "Part of my order is missing",
        "I did not receive one of the items",
        "Something is missing from the order",
    ],
    "wrong_item": [
        "I received the wrong item",
        "They sent the wrong food",
        "I asked for one thing but got something else instead",
        "My order had the wrong item",
    ],
    "payment_issue": [
        "I was charged twice for my order",
        "I got billed twice",
        "My card was charged but the order failed",
        "There is a payment issue with my order",
    ],
    "general_complaint": [
        "I am unhappy with the service",
        "This was a bad experience",
        "I want to complain about my order",
        "The overall experience was disappointing",
    ],
}


def cosine_similarity(vec_a, vec_b) -> float:
    a = np.array(vec_a, dtype=float)
    b = np.array(vec_b, dtype=float)

    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0

    return float(np.dot(a, b) / denom)


class IntentMatcher:
    def __init__(self):
        self.intent_centroids = self._build_intent_centroids()

    def _build_intent_centroids(self) -> Dict[str, List[float]]:
        centroids = {}

        for intent, examples in INTENT_EXEMPLARS.items():
            embeddings = [embed_text(example) for example in examples]
            centroid = np.mean(np.array(embeddings, dtype=float), axis=0)
            centroids[intent] = centroid.tolist()

        return centroids

    def match_intent(self, message: str) -> Tuple[str, float, Dict[str, float]]:
        message_embedding = embed_text(message)

        scores = {}
        for intent, centroid in self.intent_centroids.items():
            score = cosine_similarity(message_embedding, centroid)
            scores[intent] = round(score, 4)

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        return best_intent, best_score, scores