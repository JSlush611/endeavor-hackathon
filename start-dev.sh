#!/bin/bash

# Start the backend server
cd backend
source venv/bin/activate

# Initialize the database and load product catalog
echo "Initializing database..."
python init_db.py

# Start the backend server
python main.py &

# Start the frontend server
cd ../frontend
npm run dev &

# Wait for both processes
wait 