set -e  

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Save PIDs for proper cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Function to clean up processes on exit
cleanup() {
  echo -e "\n${YELLOW}Shutting down services...${NC}"
  
  if [ ! -z "$BACKEND_PID" ]; then
    echo "Stopping backend server (PID: $BACKEND_PID)..."
    kill -TERM $BACKEND_PID 2>/dev/null || true
  fi
  
  if [ ! -z "$FRONTEND_PID" ]; then
    echo "Stopping frontend server (PID: $FRONTEND_PID)..."
    kill -TERM $FRONTEND_PID 2>/dev/null || true
  fi
  
  echo -e "${GREEN}Cleanup complete.${NC}"
}

# Set up trap to clean up on exit
trap cleanup EXIT INT TERM

# Start from the root directory
ROOT_DIR="$(pwd)"
echo -e "${GREEN}Starting from directory: $ROOT_DIR${NC}"

# Check if we need to clean the database
CLEAN_DB=1
if [ "$1" == "--no-clean" ]; then
  CLEAN_DB=0
  echo -e "${YELLOW}Skipping database reinitialization${NC}"
fi

# Environment variables setup
export API_BASE_URL="http://localhost:8000"
export PYTHONPATH="$ROOT_DIR/backend:$PYTHONPATH"

# Check if frontend dependencies are installed
echo -e "${YELLOW}Checking frontend dependencies...${NC}"
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo -e "${YELLOW}Installing frontend dependencies...${NC}"
  cd "$ROOT_DIR/frontend"
  npm install
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install frontend dependencies. Exiting.${NC}"
    exit 1
  fi
fi

# Check if backend virtual environment exists
if [ ! -d "$ROOT_DIR/backend/venv" ]; then
  echo -e "${YELLOW}Creating backend virtual environment...${NC}"
  cd "$ROOT_DIR/backend"
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install backend dependencies. Exiting.${NC}"
    exit 1
  fi
else
  cd "$ROOT_DIR/backend"
  source venv/bin/activate
fi

# Ensure uploads directory exists
mkdir -p "$ROOT_DIR/uploads"

# Clean and initialize the database if requested
if [ $CLEAN_DB -eq 1 ]; then
  echo -e "${YELLOW}Initializing database...${NC}"
  python init_db.py
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to initialize database. Exiting.${NC}"
    exit 1
  fi
  echo -e "${GREEN}Database initialized successfully.${NC}"
fi

# Start the backend server
echo -e "${YELLOW}Starting backend server...${NC}"
python main.py &
BACKEND_PID=$!
echo -e "${GREEN}Backend server started with PID: $BACKEND_PID${NC}"

# Give the backend server some time to start up
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 3

# Start the frontend server
cd "$ROOT_DIR/frontend"
echo -e "${YELLOW}Starting frontend server...${NC}"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend server started with PID: $FRONTEND_PID${NC}"

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}Backend: http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait 