import httpx
import os
from typing import List, Dict
from models import Order, LineItem, Product, db_session
from sqlalchemy import select
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTRACTION_API_URL = "https://plankton-app-qajlk.ondigitalocean.app"
MATCHING_API_URL = "https://endeavor-interview-api-gzwki.ondigitalocean.app"

async def extract_from_pdf(file_path: str) -> List[Dict]:
    """Extract line items from PDF using the extraction API."""
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = await client.post(
                f"{EXTRACTION_API_URL}/extraction_api",
                files=files
            )
            if response.status_code != 200:
                raise Exception(f'Extraction failed: {response.text}')
            
            logger.info(f"Extraction response: {response.text}")
            return response.json()

def find_product_by_description(description: str) -> Product | None:
    """Find a product by its exact description."""
    stmt = select(Product).where(Product.description == description)
    return db_session.execute(stmt).scalar_one_or_none()

async def match_items(extracted_items: List[Dict]) -> Dict[str, List[Dict]]:
    """Match extracted items with products using the matching API."""
    # Extract just the item descriptions for matching
    item_descriptions = [item["Request Item"] for item in extracted_items]
    logger.info(f"Sending items for matching: {item_descriptions}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MATCHING_API_URL}/match/batch",
            params={"limit": 5},
            json={"queries": item_descriptions}
        )
        if response.status_code != 200:
            raise Exception(f'Matching failed: {response.text}')
        
        logger.info(f"Matching response: {response.text}")
        return response.json()['results']

async def process_order(file_path: str, filename: str) -> Order:
    """Process an uploaded order file."""
    # Initialize order variable in outer scope
    order = None
    
    try:
        # Get the order first
        stmt = select(Order).where(Order.filename == filename)
        order = db_session.execute(stmt).scalar_one_or_none()
        
        if not order:
            raise Exception("Order not found")
        
        # Extract items from PDF
        extracted_items = await extract_from_pdf(file_path)
        logger.info(f"Extracted {len(extracted_items)} items from PDF")
        
        # Match items with products
        matches_by_query = await match_items(extracted_items)
        logger.info(f"Received matches for {len(matches_by_query)} items")
        
        # Create line items
        for item_data in extracted_items:
            request_item = item_data["Request Item"]
            item_matches = matches_by_query.get(request_item, [])
            best_match = item_matches[0] if item_matches else None
            
            # Parse quantity from the extracted data
            try:
                quantity = int(item_data.get("Amount", 1))
            except (ValueError, TypeError):
                quantity = 1
            
            # Find the product ID for the best match
            matched_product = None
            if best_match:
                matched_product = find_product_by_description(best_match["match"])
                if matched_product:
                    logger.info(f"Found product {matched_product.id} for match: {best_match['match']}")
                else:
                    logger.warning(f"No product found in database for match: {best_match['match']}")
            
            line_item = LineItem(
                order_id=order.id,
                extracted_text=request_item,
                matched_product_id=matched_product.id if matched_product else None,
                confidence_score=best_match['score'] if best_match else 0.0,
                quantity=quantity
            )
            db_session.add(line_item)
            logger.info(f"Created line item: {line_item.extracted_text} (confidence: {line_item.confidence_score})")
        
        # Update order status
        order.status = 'needs_review'
        db_session.commit()
        logger.info(f"Order {order.id} processed successfully")
        
        return order
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        # If anything fails, mark the order as error
        if order:
            order.status = 'error'
            db_session.commit()
        raise e 