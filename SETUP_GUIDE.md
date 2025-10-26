# 🚀 End-to-End Setup Guide

This guide will help you set up both the backend and frontend for the USA Meme Generator.

## 📋 Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm/yarn
- OpenAI API key (required)
- Gemini API key (optional, for enhanced image generation)

## 🔧 Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd better-late-than-never/backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit with your API keys
   nano .env  # or use your preferred editor
   ```

   **Required `.env` content:**
   ```bash
   OPENAI_API_KEY=your_actual_openai_api_key_here
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   FLASK_DEBUG=True
   PORT=5000
   ```

4. **Start the backend:**
   ```bash
   ./start.sh
   # or
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

## 🎨 Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd better-late-than-never/earth-3d
   ```

2. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp env.local.example .env.local
   
   # Edit with your backend URL
   nano .env.local  # or use your preferred editor
   ```

   **Required `.env.local` content:**
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:5000
   NEXT_PUBLIC_API_TIMEOUT=30000
   NEXT_PUBLIC_DEBUG=false
   ```

3. **Install dependencies and start:**
   ```bash
   npm install
   npm run dev
   # or
   yarn install
   yarn dev
   ```

   The frontend will be available at `http://localhost:3000`

## 🧪 Testing

### Test Backend API
```bash
cd better-late-than-never/backend
python test_api.py
```

### Test Frontend Integration
1. Open `http://localhost:3000/custom/usa-meme-generator`
2. Type a prompt like "Create a funny meme about American coffee culture"
3. Watch the pipeline stages update in real-time
4. See the generated meme appear below

## 🌐 Production Deployment

### Backend Deployment
1. Update `.env` with production settings:
   ```bash
   FLASK_ENV=production
   FLASK_DEBUG=False
   PORT=5000
   ```

2. Deploy to your preferred platform (Heroku, Railway, etc.)

### Frontend Deployment
1. Update `.env.local` with your deployed backend URL:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   ```

2. Deploy to Vercel, Netlify, or your preferred platform

## 🔍 Troubleshooting

### Backend Issues
- **Missing API keys**: Check your `.env` file has correct API keys
- **Cluster data missing**: Ensure JSON files exist in the expected paths
- **Port conflicts**: Change `PORT` in `.env` if 5000 is occupied

### Frontend Issues
- **API connection failed**: Check `NEXT_PUBLIC_API_URL` in `.env.local`
- **CORS errors**: Ensure backend has CORS enabled (already configured)
- **Build errors**: Run `npm run build` to check for issues

### Debug Mode
Enable debug logging by setting:
```bash
# Backend
FLASK_DEBUG=True

# Frontend
NEXT_PUBLIC_DEBUG=true
```

## 📊 Expected Behavior

1. **User Experience:**
   - User types prompt → Pipeline appears
   - Stages update: Understanding → Concept → Text → Design
   - Generated meme (image/video) appears below

2. **Backend Processing:**
   - Content classification (image vs video)
   - Cluster selection and analysis
   - Context generation
   - Final meme creation

3. **API Response:**
   ```json
   {
     "status": "success",
     "content_type": "image",
     "data": "base64_encoded_content",
     "stages": [...]
   }
   ```

## 🎉 Success!

Once both backend and frontend are running:
- Backend: `http://localhost:5000/api/generate`
- Frontend: `http://localhost:3000/custom/usa-meme-generator`

You should see the beautiful pipeline interface with real-time stage updates and generated memes!
