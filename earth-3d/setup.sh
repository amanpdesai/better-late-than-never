#!/bin/bash

# Frontend setup script for the USA Meme Generator

echo "🎨 Setting up Frontend Environment"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the earth-3d directory."
    exit 1
fi

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    if [ -f "env.local.example" ]; then
        cp env.local.example .env.local
        echo "✅ Created .env.local from example"
        echo "🔧 Please edit .env.local to set your backend URL:"
        echo "   nano .env.local"
    else
        echo "⚠️ env.local.example not found, creating basic .env.local..."
        cat > .env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_DEBUG=false
EOF
        echo "✅ Created basic .env.local"
    fi
else
    echo "✅ .env.local already exists"
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    if command -v npm &> /dev/null; then
        npm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        echo "❌ Neither npm nor yarn found. Please install Node.js and npm/yarn."
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.local to set your backend URL"
echo "2. Start the development server:"
echo "   npm run dev"
echo "   # or"
echo "   yarn dev"
echo ""
echo "The frontend will be available at http://localhost:3000"
