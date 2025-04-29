import csv
import os
from models import Base, Product, engine, db_session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by dropping all tables and recreating them."""
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)

def load_product_catalog():
    """Load products from the CSV catalog file."""
    catalog_path = os.path.join('..', 'onsite_documents', 'unique_fastener_catalog.csv')
    
    if not os.path.exists(catalog_path):
        logger.error(f"Product catalog not found at: {catalog_path}")
        return
    
    logger.info("Loading product catalog...")
    count = 0
    
    try:
        with open(catalog_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                product = Product(
                    type=row['Type'],
                    material=row['Material'],
                    size=row['Size'],
                    length=row['Length'],
                    coating=row['Coating'],
                    thread_type=row['Thread Type'],
                    description=row['Description']
                )
                db_session.add(product)
                count += 1
                
                # Commit in batches to avoid memory issues
                if count % 1000 == 0:
                    db_session.commit()
                    logger.info(f"Loaded {count} products...")
        
        # Final commit for remaining products
        db_session.commit()
        logger.info(f"Successfully loaded {count} products")
        
    except Exception as e:
        logger.error(f"Error loading product catalog: {str(e)}")
        db_session.rollback()
        raise

def verify_database():
    """Verify that the database was initialized correctly."""
    try:
        # Check product count
        product_count = db_session.query(Product).count()
        logger.info(f"Total products in database: {product_count}")
        
        # Sample some products
        sample_products = db_session.query(Product).limit(5).all()
        logger.info("Sample products:")
        for product in sample_products:
            logger.info(f"- {product.description}")
        
        return True
    except Exception as e:
        logger.error(f"Error verifying database: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        logger.info("Starting database initialization...")
        init_db()
        load_product_catalog()
        if verify_database():
            logger.info("Database initialization completed successfully")
        else:
            logger.error("Database verification failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise 