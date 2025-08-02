@echo off
echo 🐳 Building and running BadWordDetector with Docker...

if "%1"=="build" (
    echo 🔨 Building Docker image...
    docker build -t badword-detector .
)

if "%1"=="compose" (
    echo 🚀 Starting with Docker Compose...
    docker-compose up --build
) else if "%1"=="compose-detach" (
    echo 🚀 Starting with Docker Compose (detached)...
    docker-compose up --build -d
) else if "%1"=="stop" (
    echo 🛑 Stopping Docker Compose...
    docker-compose down
) else (
    echo 🚀 Starting with Docker run...
    docker run -d --name badword-detector -p 8000:8000 -v %cd%/custom_bad_words.json:/app/custom_bad_words.json badword-detector
)

echo ✅ BadWordDetector is running!
echo 🌐 API available at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo 🔍 Health check at: http://localhost:8000/health
pause 