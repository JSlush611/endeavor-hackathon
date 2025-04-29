import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class CustomMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        self.product_descriptions = []
        self.product_ids = []
        self.tfidf_matrix = None

    def fit(self, products: List[Dict]):
        """Fit the matcher with product catalog data."""
        self.product_descriptions = []
        self.product_ids = []
        
        for product in products:
            # Create a combined text field for matching
            description = f"{product.get('description', '')} {product.get('part_number', '')} {product.get('category', '')}"
            self.product_descriptions.append(description)
            self.product_ids.append(product['id'])
        
        # Create TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.product_descriptions)
        logger.info(f"Fitted matcher with {len(products)} products")

    def match(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Match a query against the product catalog."""
        if not self.tfidf_matrix or not self.product_ids:
            raise ValueError("Matcher must be fitted with product data first")
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top k matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return list of (product_id, similarity_score) tuples
        matches = [(self.product_ids[idx], float(similarities[idx])) for idx in top_indices]
        logger.info(f"Found {len(matches)} matches for query: {query}")
        
        return matches

    def batch_match(self, queries: List[str], top_k: int = 5) -> List[List[Tuple[int, float]]]:
        """Match multiple queries against the product catalog."""
        if not self.tfidf_matrix or not self.product_ids:
            raise ValueError("Matcher must be fitted with product data first")
        
        # Transform queries to TF-IDF vectors
        query_vectors = self.vectorizer.transform(queries)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vectors, self.tfidf_matrix)
        
        # Get top k matches for each query
        matches = []
        for sim_row in similarities:
            top_indices = np.argsort(sim_row)[-top_k:][::-1]
            query_matches = [(self.product_ids[idx], float(sim_row[idx])) for idx in top_indices]
            matches.append(query_matches)
        
        logger.info(f"Processed {len(queries)} queries, found {len(matches)} sets of matches")
        return matches 