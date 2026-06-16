# JARVIS Cloud — Deploy to Railway (Free)

## Step 1 — Create GitHub repo
1. Go to github.com and create a new repo called "jarvis-cloud"
2. Upload these 3 files: app.py, requirements.txt, Procfile

## Step 2 — Deploy on Railway (Free)
1. Go to railway.app and sign up (free)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your "jarvis-cloud" repo
4. Railway will auto-detect and deploy it

## Step 3 — Set Environment Variables
In Railway dashboard → Variables, add these:
```
GROQ_API_KEY = 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
COHERE_API_KEY = 9dgMhuoyPGN23E8z508tvbRtRSTXG5Wq75QZ48hT
JARVIS_PASSWORD = jarvis2026
USERNAME = Jayden
ASSISTANT_NAME = JARVIS
SECRET_KEY = any-random-string-here
```

## Step 4 — Get your URL
Railway gives you a URL like: https://jarvis-cloud-production.up.railway.app
Open it on your phone — that's Jarvis!

## Step 5 — Add to phone home screen (optional)
On iPhone: Safari → Share → Add to Home Screen
On Android: Chrome → Menu → Add to Home Screen
It'll look like a native app with no browser bars.

## Notes
- Railway free tier: 500 hours/month (enough for always-on)
- Jarvis remembers your conversation within a session
- Voice input works on Chrome/Safari mobile
- Password: jarvis2026 (change JARVIS_PASSWORD env var to change it)
