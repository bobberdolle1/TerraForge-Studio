#!/bin/bash

# RealWorldMapGen-BNG Universal Script for Linux/Mac
# Usage: ./run.sh [start|stop|restart|status]

ACTION="${1:-start}"

show_help() {
    echo "🗺️  RealWorldMapGen-BNG Control Script"
    echo "======================================"
    echo ""
    echo "Usage:"
    echo "  ./run.sh [action]"
    echo ""
    echo "Actions:"
    echo "  start    - Start the application (default)"
    echo "  stop     - Stop the application"
    echo "  restart  - Restart the application"
    echo "  status   - Check if services are running"
    echo ""
}

get_service_status() {
    echo "🔍 Checking service status..."
    echo ""
    
    BACKEND_RUNNING=false
    FRONTEND_RUNNING=false
    
    # Check backend (port 8000)
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✓ Backend is running on port 8000"
        BACKEND_RUNNING=true
    else
        echo "✗ Backend is not running"
    fi
    
    # Check frontend (port 8080)
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✓ Frontend is running on port 8080"
        FRONTEND_RUNNING=true
    else
        echo "✗ Frontend is not running"
    fi
    
    # Check Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is running"
    else
        echo "✗ Ollama is not running"
    fi
    
    echo ""
    
    if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
        return 0
    else
        return 1
    fi
}

stop_services() {
    echo "🛑 Stopping services..."
    echo ""
    
    STOPPED=false
    
    # Try to stop tmux session
    if command -v tmux &> /dev/null; then
        if tmux has-session -t realworldmapgen 2>/dev/null; then
            tmux kill-session -t realworldmapgen
            echo "✓ Stopped tmux session"
            STOPPED=true
        fi
    fi
    
    # Try to stop screen sessions
    if command -v screen &> /dev/null; then
        if screen -list | grep -q realworldmapgen-backend; then
            screen -X -S realworldmapgen-backend quit 2>/dev/null
            echo "✓ Stopped screen backend session"
            STOPPED=true
        fi
        if screen -list | grep -q realworldmapgen-frontend; then
            screen -X -S realworldmapgen-frontend quit 2>/dev/null
            echo "✓ Stopped screen frontend session"
            STOPPED=true
        fi
    fi
    
    # Stop background processes using PID files
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "✓ Stopped backend (PID: $BACKEND_PID)"
            STOPPED=true
        fi
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "✓ Stopped frontend (PID: $FRONTEND_PID)"
            STOPPED=true
        fi
        rm .frontend.pid
    fi
    
    # Fallback: kill by port
    if command -v lsof &> /dev/null; then
        BACKEND_PID=$(lsof -ti:8000)
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null
            echo "✓ Stopped process on port 8000"
            STOPPED=true
        fi
        
        FRONTEND_PID=$(lsof -ti:8080)
        if [ ! -z "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null
            echo "✓ Stopped process on port 8080"
            STOPPED=true
        fi
    fi
    
    echo ""
    if [ "$STOPPED" = true ]; then
        echo "✅ Services stopped"
    else
        echo "ℹ️  No services were running"
    fi
}

start_services() {
    echo "🗺️  RealWorldMapGen-BNG"
    echo "================================"
    echo ""
    
    # Check Python
    echo "🔍 Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.13+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
    echo ""
    
    # Check Poetry
    echo "🔍 Checking Poetry installation..."
    if ! command -v poetry &> /dev/null; then
        echo "❌ Poetry is not installed. Installing Poetry..."
        echo ""
        curl -sSL https://install.python-poetry.org | python3 -
        echo ""
        echo "⚠️  Please restart your terminal and run this script again."
        echo "   Poetry needs to be in your PATH."
        exit 0
    fi
    
    echo "✓ Poetry found"
    echo ""
    
    # Check .env
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✓ .env file created"
        else
            echo "❌ .env.example not found"
            exit 1
        fi
        echo ""
    fi
    
    # Create directories
    mkdir -p output cache
    
    # Check dependencies
    echo "🔍 Checking dependencies..."
    NEEDS_INSTALL=false
    
    if [ ! -f poetry.lock ]; then
        NEEDS_INSTALL=true
        echo "   Dependencies not installed yet"
    else
        if [ pyproject.toml -nt poetry.lock ]; then
            NEEDS_INSTALL=true
            echo "   Dependencies need update"
        fi
    fi
    
    if [ "$NEEDS_INSTALL" = true ]; then
        echo ""
        echo "📦 Installing Python dependencies..."
        echo "   This may take a few minutes on first run..."
        poetry install
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install dependencies"
            exit 1
        fi
        echo "✓ Dependencies installed"
        echo ""
    else
        echo "✓ Dependencies are up to date"
        echo ""
    fi
    
    # Check Ollama
    echo "🔍 Checking Ollama status..."
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "⚠️  Ollama is not running!"
        echo "   Please start Ollama in another terminal: ollama serve"
        echo ""
        read -p "Press Enter once Ollama is running, or Ctrl+C to cancel..."
    fi
    echo "✓ Ollama is running"
    echo ""
    
    echo "🚀 Starting services..."
    echo ""
    
    # Start with tmux if available
    if command -v tmux &> /dev/null; then
        echo "📡 Using tmux to start services..."
        echo ""
        
        SESSION_NAME="realworldmapgen"
        tmux kill-session -t $SESSION_NAME 2>/dev/null
        
        tmux new-session -d -s $SESSION_NAME -n backend "cd '$PWD' && poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000"
        tmux new-window -t $SESSION_NAME -n frontend "cd '$PWD/frontend' && python3 -m http.server 8080"
        
        echo "✅ Services started in tmux session: $SESSION_NAME"
        echo ""
        echo "🌐 Access the application at:"
        echo "   Frontend: http://localhost:8080"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📝 Useful commands:"
        echo "   View services:  tmux attach -t $SESSION_NAME"
        echo "   Stop services:  ./run.sh stop"
        echo ""
        
    elif command -v screen &> /dev/null; then
        echo "📡 Using screen to start services..."
        echo ""
        
        screen -dmS realworldmapgen-backend bash -c "cd '$PWD' && poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000"
        screen -dmS realworldmapgen-frontend bash -c "cd '$PWD/frontend' && python3 -m http.server 8080"
        
        echo "✅ Services started in screen sessions"
        echo ""
        echo "🌐 Access the application at:"
        echo "   Frontend: http://localhost:8080"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📝 Useful commands:"
        echo "   View backend:   screen -r realworldmapgen-backend"
        echo "   Stop services:  ./run.sh stop"
        echo ""
        
    else
        echo "📡 Starting in background..."
        echo ""
        
        cd "$PWD"
        poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > .backend.pid
        echo "📡 Backend started (PID: $BACKEND_PID)"
        
        cd "$PWD/frontend"
        python3 -m http.server 8080 > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../.frontend.pid
        echo "🌐 Frontend started (PID: $FRONTEND_PID)"
        
        cd "$PWD"
        
        echo ""
        echo "✅ Services started in background"
        echo ""
        echo "🌐 Access the application at:"
        echo "   Frontend: http://localhost:8080"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📝 Useful commands:"
        echo "   View backend logs:  tail -f backend.log"
        echo "   Stop services:      ./run.sh stop"
        echo ""
    fi
}

# Main execution
case "$ACTION" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        echo "🔄 Restarting services..."
        echo ""
        stop_services
        echo ""
        sleep 2
        start_services
        ;;
    status)
        get_service_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown action: $ACTION"
        echo ""
        show_help
        exit 1
        ;;
esac
