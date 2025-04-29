from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import os
import shutil
from typing import List
import services
from models import Order, LineItem, db_session, Base, engine, Product
from sqlalchemy import select
import logging
from datetime import datetime
from init_db import init_db, load_product_catalog, verify_database
import io
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/cleanup")
async def cleanup_system():
    """Clear the database and uploads directory, then reload the product catalog."""
    try:
        logger.info("Starting system cleanup...")
        
        # Initialize database (drops and recreates tables)
        init_db()
        logger.info("Database tables recreated")
        
        # Load product catalog
        load_product_catalog()
        if verify_database():
            logger.info("Product catalog reloaded successfully")
        else:
            raise Exception("Failed to verify database after loading product catalog")
        
        # Clear uploads directory
        for file in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        logger.info("Uploads directory cleared")
        
        return {"message": "System cleaned up and product catalog reloaded successfully"}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_unique_filename(filename: str) -> str:
    """Generate a unique filename by adding a timestamp if needed."""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}{ext}"

async def process_uploaded_file(file_path: str, file_name: str):
    """Background task to process the uploaded file."""
    try:
        logger.info(f"Starting to process file: {file_name}")
        await services.process_order(file_path, file_name)
        logger.info(f"Successfully processed file: {file_name}")
    except Exception as e:
        logger.error(f"Error processing file {file_name}: {str(e)}")
        # Get the order and update its status
        stmt = select(Order).where(Order.filename == file_name)
        order = db_session.execute(stmt).scalar_one_or_none()
        if order:
            order.status = 'error'
            db_session.commit()
            logger.info(f"Updated order status to error for file: {file_name}")
        raise e

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Handle file upload and initiate processing."""
    logger.info(f"Received upload request for file: {file.filename}")
    
    if not file.filename.lower().endswith('.pdf'):
        logger.warning(f"Rejected non-PDF file: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Use original filename for API compatibility
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Removed existing file: {file_path}")
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Saved uploaded file to: {file_path}")
    
    try:
        # Delete any existing order with this filename
        stmt = select(Order).where(Order.filename == file.filename)
        existing_order = db_session.execute(stmt).scalar_one_or_none()
        if existing_order:
            db_session.delete(existing_order)
            db_session.commit()
            logger.info(f"Deleted existing order for file: {file.filename}")
        
        # Create new order record
        order = Order(filename=file.filename, status='processing')
        db_session.add(order)
        db_session.commit()
        logger.info(f"Created new order record for file: {file.filename}")
        
        # Start processing in background
        background_tasks.add_task(process_uploaded_file, file_path, file.filename)
        logger.info(f"Started background processing for file: {file.filename}")
        
        return {"id": order.id, "status": order.status}
    except Exception as e:
        logger.error(f"Error handling upload for file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
async def list_orders() -> List[dict]:
    """List all orders."""
    stmt = select(Order)
    orders = db_session.execute(stmt).scalars().all()
    return [{"id": o.id, "filename": o.filename, "status": o.status, 
             "created_at": o.created_at.isoformat(), 
             "updated_at": o.updated_at.isoformat()} for o in orders]

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order details including line items."""
    stmt = select(Order).where(Order.id == order_id)
    order = db_session.execute(stmt).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order": {
            "id": order.id,
            "filename": order.filename,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        },
        "line_items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "extracted_text": item.extracted_text,
                "matched_product_id": item.matched_product_id,
                "confidence_score": item.confidence_score
            }
            for item in order.line_items
        ]
    }

@app.post("/orders/{order_id}/line-items/{item_id}")
async def update_line_item(order_id: int, item_id: int, product_id: int):
    """Update a line item's matched product."""
    stmt = select(LineItem).where(LineItem.id == item_id, LineItem.order_id == order_id)
    line_item = db_session.execute(stmt).scalar_one_or_none()
    if not line_item:
        raise HTTPException(status_code=404, detail="Line item not found")
    
    line_item.matched_product_id = product_id
    db_session.commit()
    
    return {
        "id": line_item.id,
        "order_id": line_item.order_id,
        "extracted_text": line_item.extracted_text,
        "matched_product_id": line_item.matched_product_id,
        "confidence_score": line_item.confidence_score
    }

@app.get("/orders/{order_id}/export")
async def export_order(order_id: int):
    """Export order details as CSV."""
    # Get order and line items
    stmt = select(Order).where(Order.id == order_id)
    order = db_session.execute(stmt).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Line Item ID", "Extracted Text", "Matched Product ID",
        "Product Description", "Product Type", "Material",
        "Size", "Length", "Coating", "Thread Type",
        "Quantity", "Confidence Score"
    ])
    
    # Write data
    for item in order.line_items:
        product = None
        if item.matched_product_id:
            stmt = select(Product).where(Product.id == item.matched_product_id)
            product = db_session.execute(stmt).scalar_one_or_none()
        
        writer.writerow([
            item.id,
            item.extracted_text,
            item.matched_product_id or "",
            product.description if product else "",
            product.type if product else "",
            product.material if product else "",
            product.size if product else "",
            product.length if product else "",
            product.coating if product else "",
            product.thread_type if product else "",
            item.quantity,
            f"{item.confidence_score:.2f}"
        ])
    
    # Prepare the response
    output.seek(0)
    filename = f"order_{order.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv",
    }
    
    return StreamingResponse(
        iter([output.getvalue()]),
        headers=headers,
        media_type="text/csv"
    )

@app.post("/orders/{order_id}/status")
async def update_order_status(order_id: int, status_data: dict = Body(...)):
    """Update order status."""
    status = status_data.get('status')
    if not status or status not in ['processing', 'needs_review', 'completed', 'error']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    stmt = select(Order).where(Order.id == order_id)
    order = db_session.execute(stmt).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db_session.commit()
    
    return {
        "id": order.id,
        "filename": order.filename,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat()
    }

@app.get("/products/search")
async def search_products(q: str):
    """Search products by description."""
    # Use a simple LIKE query for fuzzy matching
    stmt = select(Product).where(Product.description.ilike(f"%{q}%")).limit(10)
    products = db_session.execute(stmt).scalars().all()
    return [
        {
            "id": p.id,
            "description": p.description,
            "category": p.type,  # Using type as category
            "unit_price": p.unit_price,
            "material": p.material,
            "size": p.size,
            "length": p.length,
            "coating": p.coating,
            "thread_type": p.thread_type
        }
        for p in products
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 