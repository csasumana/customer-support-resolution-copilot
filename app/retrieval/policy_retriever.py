from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

from app.retrieval.embedder import embed_text
from app.retrieval.policy_loader import load_policies


class PolicyRetriever:
    def __init__(self):
        self.policies = load_policies()
        self.policy_embeddings = [embed_text(policy["text"]) for policy in self.policies]

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict]:
        query_embedding = embed_text(query)

        similarity_scores = cosine_similarity([query_embedding], self.policy_embeddings)[0]

        ranked = sorted(
            zip(self.policies, similarity_scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for policy, score in ranked[:top_k]:
            results.append(
                {
                    "name": policy["name"],
                    "text": policy["text"],
                    "score": float(score),
                }
            )

        return results