# Sales Order Processing Automation

An end-to-end solution for automating the processing of sales order documents. This application streamlines the workflow of uploading, extracting, matching, verifying, and exporting sales orders.

## Overview

This application automates the traditionally manual process of handling sales order documents. It eliminates the bottleneck of manually entering data from purchase orders into systems by providing a seamless workflow:

1. **Upload**: Users can drag and drop PDF sales orders
2. **Extract**: The system automatically extracts line items from the document
3. **Match**: Each line item is intelligently matched to products in the catalog
4. **Verify**: Users can review and correct matches through an intuitive interface
5. **Export**: Finalized orders can be exported as structured CSV files

## Features

### Core Functionality
- **PDF Upload System**: Drag-and-drop interface with progress tracking
- **Automated Extraction**: Integration with PDF Extraction API
- **Intelligent Matching**: Product matching using a specialized matching API
- **Human-in-the-Loop Review**: Interactive interface for reviewing and adjusting matches
- **Data Export**: Export processed orders as CSV files

### Dashboard & Management
- **Order Dashboard**: View all processed orders and their statuses
- **Order Details View**: Detailed view of each order with line items and matches
- **Status Tracking**: Visual indicators for order processing status
- **Confidence Scoring**: Visual indicators for match confidence levels

### User Experience
- **Real-time Search**: Type-ahead search for product matching
- **Toast Notifications**: Success and error feedback throughout the application
- **Responsive Design**: Clean, intuitive interface that works across devices
- **Loading States**: Visual feedback during processing operations

### Backend Architecture
- **FastAPI Backend**: High-performance, asynchronous API
- **SQLite Database**: Efficient data storage with SQLAlchemy ORM
- **Background Processing**: Asynchronous processing of uploaded documents
- **Error Handling**: Comprehensive error handling and status tracking

## Tech Stack

### Frontend
- React
- Tailwind CSS
- TypeScript
- React Router
- React Dropzone
- Headless UI

### Backend
- FastAPI
- SQLAlchemy
- HTTPX for async API requests
- SQLite
- Python 3.10+

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 14 or higher
- npm or yarn

### Quick Start
We've provided a convenient script to set up and run the application:

```bash
# Make the script executable
chmod +x start-dev.sh

# Run the application (will initialize database)
./start-dev.sh

# To run without reinitializing the database
./start-dev.sh --no-clean
```

### Manual Setup

If you prefer to set things up manually:

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start the backend server
python main.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Using the Application

1. Access the frontend at `http://localhost:5173`
2. Upload a PDF file from the "Upload Order" page
3. Once processed, the order will appear in the dashboard
4. Click on an order to review its details
5. Review and edit product matches as needed
6. Mark the order as completed when finished
7. Export the order data as CSV

## Design Decisions

### Modular Component Architecture
We built the frontend using a modular component approach with reusable UI elements like `Card`, `Button`, and `Toast` to ensure consistency and maintainability.

### Human-in-the-Loop Design
While the system automates matching, we recognized the importance of human oversight. The interface allows users to easily review and correct matches, leveraging both AI capabilities and human expertise.

### Asynchronous Processing
The backend uses asynchronous processing to handle document extraction and product matching, ensuring the UI remains responsive even during complex operations.

### Progressive Enhancement
The application provides immediate feedback at each step, from upload progress indicators to toast notifications, enhancing the user experience.

### Data Persistence
We implemented a robust database schema using SQLAlchemy to ensure all processed orders and edits persist across sessions.

### Error Handling and Recovery
The system includes comprehensive error handling at each stage, with clear status indicators and the ability to retry or manually correct failures.

## Extra Features

### Toast Notification System
We implemented a custom toast notification system for providing feedback on actions like uploads, matches, and completions, enhancing the user experience.

### Real-time Product Search
The product matching interface includes a real-time search with debouncing, making it easy to find the right product matches quickly.

### Confidence Score Visualization
Each matched product displays a confidence score with color coding to help users quickly identify matches that may need review.

### Batch Database Initialization
The database initialization process uses batch processing to efficiently load the product catalog, handling large datasets without memory issues.

### Graceful Process Management
Our start script includes proper process management with signal handling, ensuring clean shutdowns and preventing orphaned processes.

## Known Limitations and Future Improvements

- **Advanced Matching Algorithm**: Future versions could implement a custom matching algorithm with additional heuristics
- **Bulk Operations**: Adding support for batch uploading and processing multiple documents
- **User Authentication**: Implementing user accounts and role-based access
- **Analytics Dashboard**: Adding statistics and insights about processing accuracy and efficiency
- **Mobile Optimization**: Further enhancing the mobile experience for field use

## Troubleshooting

### Common Issues

**Backend fails to start**
- Ensure port 8000 is not already in use
- Check that all dependencies are installed correctly
- Verify that the database file is not corrupted

**Frontend fails to start**
- Ensure port 5173 is not already in use
- Verify that node_modules are installed correctly

**PDF Upload Fails**
- Ensure the PDF file has a valid format
- Check that the backend server is running
- Verify that the uploads directory exists and is writable

**Product Matching Fails**
- Check network connectivity to the matching API
- Verify that the product catalog is properly loaded
- Examine the backend logs for specific error messages

## Support

For issues or questions, please create a GitHub issue in this repository.

---

Built for the Endeavor AI Hackathon Challenge. 