#!/bin/bash

# DokushoCafe Development Server Startup Script

echo "🌸 Starting DokushoCafe (読書カフェ) Development Server 🌸"
echo "================================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if Django is installed
python -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Django not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run migrations if needed
echo "🔄 Checking for database migrations..."
python manage.py migrate --check 2>/dev/null
if [ $? -ne 0 ]; then
    echo "🔧 Applying database migrations..."
    python manage.py migrate
fi

# Start development server
echo "🚀 Starting development server..."
echo "📱 Open your browser and go to: http://localhost:8000"
echo "⚙️  Admin panel available at: http://localhost:8000/admin"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python manage.py runserver