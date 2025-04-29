import httpx
import os
from typing import List, Dict, Tuple, Any
from models import Order, LineItem, Product, db_session
from sqlalchemy import select
import logging
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from .matching import CustomMatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTRACTION_API_URL = "https://plankton-app-qajlk.ondigitalocean.app"
MATCHING_API_URL = "https://endeavor-interview-api-gzwki.ondigitalocean.app"

# Initialize the custom matcher
matcher = CustomMatcher()

async def extract_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract items from PDF using the extraction API."""
    try:
        async with httpx.AsyncClient() as client:
            with open(pdf_path, 'rb') as f:
                files = {'file': ('document.pdf', f, 'application/pdf')}
                response = await client.post(
                    'http://localhost:5000/extract',
                    files=files
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Extracted {len(data.get('items', []))} items from PDF")
                return data.get('items', [])
    except Exception as e:
        logger.error(f"Error extracting from PDF: {str(e)}")
        raise

def find_product_by_description(description: str) -> Product | None:
    """Find a product by its exact description."""
    stmt = select(Product).where(Product.description == description)
    return db_session.execute(stmt).scalar_one_or_none()

def calculate_fuzzy_score(text1: str, text2: str) -> float:
    """Calculate fuzzy matching score using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def calculate_feature_score(item: str, product: Product) -> float:
    """Calculate score based on product features."""
    features = [
        product.material,
        product.size,
        product.length,
        product.coating,
        product.thread_type
    ]
    feature_scores = [calculate_fuzzy_score(item, f) for f in features if f]
    return np.mean(feature_scores) if feature_scores else 0

def calculate_semantic_score(item: str, product: Product, vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray) -> float:
    """Calculate semantic similarity using TF-IDF and cosine similarity."""
    item_vector = vectorizer.transform([item])
    product_vector = vectorizer.transform([product.description])
    return cosine_similarity(item_vector, product_vector)[0][0]

def get_best_matches(extracted_items: List[str], top_k: int = 5) -> List[Dict]:
    """Find the best matches for extracted items using a combination of matching algorithms."""
    try:
        # Get all products from database
        stmt = select(Product)
        products = db_session.execute(stmt).scalars().all()
        
        if not products:
            logger.error("No products found in database")
            return []

        # Prepare TF-IDF vectors for semantic matching
        product_descriptions = [p.description for p in products]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(product_descriptions)

        results = []
        for item in extracted_items:
            matches = []
            for product in products:
                # Calculate different similarity scores
                fuzzy_score = calculate_fuzzy_score(item, product.description)
                feature_score = calculate_feature_score(item, product)
                semantic_score = calculate_semantic_score(item, product, vectorizer, tfidf_matrix)

                # Combine scores with weights
                combined_score = (
                    0.4 * fuzzy_score +  # Text similarity
                    0.3 * feature_score +  # Feature matching
                    0.3 * semantic_score  # Semantic similarity
                )

                matches.append({
                    'product_id': product.id,
                    'description': product.description,
                    'category': product.type,
                    'material': product.material,
                    'size': product.size,
                    'length': product.length,
                    'coating': product.coating,
                    'thread_type': product.thread_type,
                    'unit_price': product.unit_price,
                    'confidence_score': combined_score * 100,  # Convert to percentage
                    'match_details': {
                        'text_similarity': fuzzy_score * 100,
                        'feature_match': feature_score * 100,
                        'semantic_similarity': semantic_score * 100
                    }
                })

            # Sort by combined score and get top matches
            matches.sort(key=lambda x: x['confidence_score'], reverse=True)
            results.append({
                'extracted_text': item,
                'matches': matches[:top_k]
            })

        return results

    except Exception as e:
        logger.error(f"Error in custom matching: {str(e)}")
        raise

async def match_items(extracted_items: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """Match extracted items against product catalog using custom matcher."""
    try:
        # Get all products from database
        products = db.execute("SELECT id, description, part_number, category FROM products").fetchall()
        products = [dict(row) for row in products]
        
        # Fit the matcher with product data
        matcher.fit(products)
        
        # Extract descriptions for matching
        queries = [item.get('Request Item', '') for item in extracted_items]
        
        # Get matches for all items
        matches = matcher.batch_match(queries)
        
        # Format results
        results = []
        for item, item_matches in zip(extracted_items, matches):
            matched_products = []
            for product_id, score in item_matches:
                product = next((p for p in products if p['id'] == product_id), None)
                if product:
                    matched_products.append({
                        'id': product_id,
                        'description': product['description'],
                        'part_number': product['part_number'],
                        'confidence': score
                    })
            
            results.append({
                'extracted_text': item.get('Request Item', ''),
                'quantity': item.get('Quantity', 0),
                'matches': matched_products
            })
        
        logger.info(f"Matched {len(results)} items against product catalog")
        return results
    except Exception as e:
        logger.error(f"Error matching items: {str(e)}")
        raise

async def process_order(order_id: int, db: Session):
    """Process an order through the pipeline."""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Update status to processing
        order.status = OrderStatus.PROCESSING
        db.commit()
        
        # Extract items from PDF
        extracted_items = await extract_from_pdf(order.file_path)
        
        # Match items against product catalog
        matched_items = await match_items(extracted_items, db)
        
        # Create line items
        for item in matched_items:
            line_item = LineItem(
                order_id=order_id,
                extracted_text=item['extracted_text'],
                quantity=item['quantity'],
                matches=item['matches']
            )
            db.add(line_item)
        
        # Update order status
        order.status = OrderStatus.PENDING_REVIEW
        db.commit()
        
        logger.info(f"Successfully processed order {order_id}")
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {str(e)}")
        order.status = OrderStatus.ERROR
        db.commit()
        raise 