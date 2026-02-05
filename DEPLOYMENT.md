# Deployment Guide

## Vercel Deployment

### Prerequisites
- Vercel account (https://vercel.com)
- Vercel CLI installed: `npm install -g vercel`

### Important Limitations

⚠️ **Vercel Limitations for This Application:**

1. **Stateless Functions**: Vercel serverless functions are stateless. The in-memory `sessions` dictionary will NOT persist between requests.
2. **Cold Starts**: Functions may experience cold starts, causing delays.
3. **Timeout Limits**: Vercel has a 10-second timeout for Hobby plan, 60 seconds for Pro.
4. **No WebSockets**: Real-time features are limited.

**Recommendation**: For production use with session persistence, consider:
- **Railway** (https://railway.app) - Better for stateful apps
- **Render** (https://render.com) - Good for FastAPI
- **Google Cloud Run** - Serverless containers
- **AWS ECS/Fargate** - Full container orchestration

### Vercel Deployment Steps

If you still want to deploy to Vercel (for testing/demo purposes):

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Set Environment Variables
In your Vercel dashboard or via CLI:

```bash
vercel env add GROQ_API_KEY
# Paste your Groq API key

vercel env add API_KEY
# Paste your honeypot API key

vercel env add GUVI_ENDPOINT
# Paste the GUVI endpoint URL (optional)
```

#### 3. Deploy
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? `ai-honeypot`
- In which directory is your code located? `./`

#### 4. Production Deployment
```bash
vercel --prod
```

### Alternative: Railway Deployment (Recommended)

Railway is better suited for this application because it supports:
- Stateful applications
- Longer timeouts
- Persistent storage options
- Docker containers

#### Railway Setup

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login**
```bash
railway login
```

3. **Initialize Project**
```bash
railway init
```

4. **Add Environment Variables**
```bash
railway variables set GROQ_API_KEY=your_key_here
railway variables set API_KEY=your_api_key_here
railway variables set GUVI_ENDPOINT=your_endpoint_here
```

5. **Deploy**
```bash
railway up
```

Railway will automatically detect the Dockerfile and deploy your application!

### Alternative: Render Deployment

1. Create a `render.yaml`:
```yaml
services:
  - type: web
    name: ai-honeypot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: API_KEY
        sync: false
      - key: GUVI_ENDPOINT
        sync: false
```

2. Connect your GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy!

## Production Considerations

### Session Management
For production, replace in-memory sessions with:

**Redis** (recommended):
```python
import redis
from redis import Redis

redis_client = Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    decode_responses=True
)

# Store session
redis_client.setex(
    f"session:{session_id}",
    3600,  # 1 hour TTL
    json.dumps(session_data)
)

# Retrieve session
session_data = json.loads(
    redis_client.get(f"session:{session_id}")
)
```

**PostgreSQL/MongoDB**:
- Store sessions in a database
- Better for long-term analytics
- Allows querying historical data

### Monitoring
Add monitoring tools:
- **Sentry** for error tracking
- **Datadog/New Relic** for performance
- **Prometheus + Grafana** for metrics

### Rate Limiting
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/honeypot")
@limiter.limit("10/minute")
async def handle_message(...):
    ...
```

### Security
- Use HTTPS only
- Rotate API keys regularly
- Implement IP whitelisting if needed
- Add request validation
- Use environment-specific configs

## Cost Estimates

### Vercel
- **Hobby**: Free (limited)
- **Pro**: $20/month

### Railway
- **Free**: $5 credit/month
- **Developer**: $5/month + usage

### Render
- **Free**: Limited resources
- **Starter**: $7/month

### Recommended: Railway or Render for this application
