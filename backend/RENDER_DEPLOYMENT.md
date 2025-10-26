# 🚀 Render Deployment Guide

Simple deployment guide for Render.com

## 📋 Prerequisites

- GitHub repository with the backend code
- Render.com account
- OpenAI API key
- Gemini API key (optional)

## 🔧 Render Setup

1. **Connect Repository**
   - Go to Render.com dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `better-late-than-never/backend` folder

2. **Configure Service**
   - **Name**: `meme-generator-backend` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Environment Variables**
   Add these in Render dashboard under "Environment":
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_ENV=production
   FLASK_DEBUG=False
   PORT=10000
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your API will be available at `https://your-service-name.onrender.com`

## 🔗 Frontend Configuration

Update your frontend `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://your-service-name.onrender.com
```

## ✅ That's It!

Your backend is now deployed on Render and ready to use!
