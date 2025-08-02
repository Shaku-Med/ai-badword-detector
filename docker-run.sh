#!/bin/bash

echo "🐳 Building and running BadWordDetector with Docker..."

if [ "$1" = "build" ]; then
    echo "🔨 Building Docker image..."
    docker build -t badword-detector .
fi

if [ "$1" = "compose" ]; then
    echo "🚀 Starting with Docker Compose..."
    docker-compose up --build
elif [ "$1" = "compose-detach" ]; then
    echo "🚀 Starting with Docker Compose (detached)..."
    docker-compose up --build -d
elif [ "$1" = "stop" ]; then
    echo "🛑 Stopping Docker Compose..."
    docker-compose down
else
    echo "🚀 Starting with Docker run..."
    docker run -d \
        --name badword-detector \
        -p 8000:8000 \
        -v $(pwd)/custom_bad_words.json:/app/custom_bad_words.json \
        badword-detector
fi

echo "✅ BadWordDetector is running!"
echo "🌐 API available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health" 