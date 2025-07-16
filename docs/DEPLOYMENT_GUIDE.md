# Deployment Guide - Render.com

## Overview

This guide provides step-by-step instructions for deploying the Plant Database API to render.com for production use. The deployment includes environment configuration, security setup, and monitoring.

## Prerequisites

### Required Accounts & Services
- **Render.com account** (free tier available)
- **Google Cloud Platform account** with Sheets API enabled
- **GitHub repository** with your Plant Database API code
- **Google Sheets document** with plant data

### Required Files
Ensure these files are present in your repository:
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `api/main.py` - Flask application entry point
- Environment variables configuration

## Pre-Deployment Setup

### 1. Google Sheets API Configuration

**Create Service Account**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing one
3. Enable Google Sheets API
4. Create Service Account credentials
5. Download JSON key file (keep secure!)

**Configure Google Sheet**:
1. Create or prepare your plant database sheet
2. Share sheet with service account email (from JSON key)
3. Note the Spreadsheet ID from the URL
4. Verify sheet has proper headers (see field_config.py)

### 2. Environment Variables

Create a `.env` file locally for testing (DO NOT commit to git):
```bash
# Google Sheets Configuration
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", "project_id": "your-project", ...}
SPREADSHEET_ID=your_spreadsheet_id_here
SHEET_GID=0

# API Security
GARDENLLM_API_KEY=your_secure_api_key_here

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_key_here

# Production Rate Limiting (optional but recommended)
REDIS_URL=redis://your_redis_url:6379
```

### 3. Redis Setup (Production Recommended)

For production-grade rate limiting, set up Redis:

**Option A: Render.com Redis (Recommended)**
1. In Render dashboard, click **"New +"** → **"Key Value"**
2. Configure Redis service:
   - **Name**: `plant-api-redis`
   - **Plan**: "Starter" (free tier)
   - **Region**: Same as your web service
3. Copy the **Internal Redis URL** (format: `redis://red-xxxxx:6379`)
4. Add to web service environment variables: `REDIS_URL=[Internal Redis URL]`

**Option B: External Redis Provider**
- **Upstash Redis**: Free tier available, easy setup
- **Redis Cloud**: Managed Redis service
- **Railway**: Simple Redis deployment

**Without Redis**: API automatically falls back to in-memory storage with warning logs (functional but not recommended for production).

**Benefits of Redis**:
- Persistent rate limiting across server restarts
- Shared state across multiple API instances
- Better performance under load
- Production-ready scalability

### 4. Requirements File

Verify `requirements.txt` contains updated dependencies:
```
# Core Flask and API dependencies
Flask==3.1.1
flask-cors==6.0.1
Flask-Limiter==3.12
gunicorn==23.0.0
python-dotenv==1.1.1
requests==2.32.4

# Google Sheets API dependencies
google-api-python-client==2.176.0
google-auth==2.40.3
google-auth-httplib2==0.2.0

# Rate limiting storage (Redis for production)
redis==5.2.1

# Testing dependencies
pytest==8.4.1

# OpenAI for potential future integrations
openai==1.96.0

# Core Python dependencies
urllib3==2.5.0
certifi==2025.7.14
charset-normalizer==3.4.2
idna==3.10
```

**Note**: Deprecated dependencies like `pytz`, `typing-inspection`, and unnecessary packages have been removed for better security and performance.

### 4. Runtime Configuration

Create `runtime.txt` in project root:
```
python-3.11.0
```

## Render.com Deployment

### Step 1: Create New Web Service

1. **Login to Render.com**
2. **Click "New +"** → "Web Service"
3. **Connect GitHub Repository**
   - Authorize Render to access your GitHub
   - Select your plant-database-api repository

### Step 2: Configure Service Settings

**Basic Configuration**:
- **Name**: `plant-database-api` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3.11.0`

**Build Configuration**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m api.main`

### Step 3: Environment Variables Setup

In Render.com dashboard, add these environment variables:

**Required Variables**:
```
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", "project_id": "your-project", "private_key_id": "your-key-id", "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n", "client_email": "your-service-account@your-project.iam.gserviceaccount.com", "client_id": "your-client-id", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "your-cert-url"}

SPREADSHEET_ID=1zmKVuDTbgColGuoHJDF0ZJxXB6N2WfwLkp7LZ0vqOag

SHEET_GID=0

GARDENLLM_API_KEY=your_secure_32_character_api_key_here
```

**Optional Variables**:
```
OPENAI_API_KEY=sk-your-openai-key-here

FLASK_ENV=production

CORS_ORIGINS=https://yourdomain.com,https://anotherdomain.com
```

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Monitor deployment logs** in real-time
3. **Wait for "Your service is live"** message
4. **Note your service URL**: `https://your-service-name.onrender.com`

## Post-Deployment Configuration

### 1. Test API Endpoints

**Health Check**:
```bash
curl https://your-service-name.onrender.com/
```
Expected response:
```json
{
  "status": "ok",
  "message": "Plant Database API is running."
}
```

**Test Plant Retrieval**:
```bash
curl https://your-service-name.onrender.com/api/plants
```

**Test Authenticated Endpoint**:
```bash
curl -X POST https://your-service-name.onrender.com/api/plants \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{"Plant Name": "Test Plant", "Location": "Test Garden"}'
```

### 2. Configure Custom Domain (Optional)

**Add Custom Domain**:
1. Go to your service dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain (e.g., `api.yourgarden.com`)
4. Configure DNS CNAME record:
   ```
   CNAME api your-service-name.onrender.com
   ```
5. SSL certificate will be automatically provisioned

### 3. Set Up Monitoring

**Health Check Monitoring**:
- Render provides automatic health checks on your service URL
- Configure external monitoring (e.g., UptimeRobot) for additional reliability

**Log Monitoring**:
- Access logs via Render dashboard
- Consider log aggregation service for production

## Security Configuration

### 1. API Key Management

**Generate Secure API Key**:
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"Generated API Key: {api_key}")
```

**Key Rotation Strategy**:
- Rotate API keys monthly
- Use separate keys for different clients/applications
- Monitor key usage in audit logs

### 2. CORS Configuration

For web applications, configure CORS origins:
```python
# In your environment variables
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 3. Rate Limiting

Default rate limits are configured:
- **Write operations**: 10 requests per minute
- Adjust in `api/main.py` if needed for your use case

## Environment-Specific Configuration

### Production Environment Variables

```bash
# Production-only settings
FLASK_ENV=production
DEBUG=False
TESTING=False

# Enhanced security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn-here
```

### Development vs Production Differences

| Setting | Development | Production |
|---------|-------------|------------|
| Debug Mode | True | False |
| Rate Limiting | Disabled | Enabled |
| SSL Redirect | False | True |
| Log Level | DEBUG | INFO |
| Error Details | Full | Minimal |

## Troubleshooting

### Common Deployment Issues

**Build Failures**:
```
Error: Failed to install requirements
```
**Solution**: Verify `requirements.txt` syntax and package versions

**Google Sheets API Errors**:
```
Error: Credentials not found
```
**Solution**: 
1. Verify `GOOGLE_APPLICATION_CREDENTIALS_JSON` is properly formatted
2. Ensure service account has access to the spreadsheet
3. Check Sheets API is enabled in Google Cloud Console

**Authentication Issues**:
```
Error: Unauthorized
```
**Solution**:
1. Verify `GARDENLLM_API_KEY` environment variable is set
2. Check API key in request headers: `x-api-key`

**Rate Limiting Problems**:
```
Error: Too Many Requests
```
**Solution**: Implement exponential backoff in client applications

### Debug Commands

**Check Environment Variables**:
```python
import os
print("API Key configured:", bool(os.environ.get('GARDENLLM_API_KEY')))
print("Spreadsheet ID:", os.environ.get('SPREADSHEET_ID', 'Not configured'))
```

**Test Google Sheets Connection**:
```python
from config.config import sheets_client, SPREADSHEET_ID
result = sheets_client.values().get(spreadsheetId=SPREADSHEET_ID, range='Plants!A1:A1').execute()
print("Connection successful:", bool(result))
```

## Performance Optimization

### 1. Caching Strategy

**Plant List Caching**:
- 5-minute cache for plant lists
- Automatic cache invalidation on updates
- Consider Redis for production caching

### 2. Database Optimization

**Google Sheets Optimization**:
- Minimize API calls with batch operations
- Use appropriate value render options
- Implement request rate limiting

### 3. Response Optimization

**JSON Response Optimization**:
- Minimize response payload size
- Use appropriate HTTP status codes
- Implement response compression

## Scaling Considerations

### Resource Requirements

**Render.com Plans**:
- **Free Plan**: Suitable for development/testing
- **Starter Plan ($7/month)**: Recommended for production
- **Standard Plan ($25/month)**: For high-traffic applications

**Resource Monitoring**:
- Monitor CPU and memory usage
- Track response times
- Monitor error rates

### Load Balancing

For high-traffic scenarios:
1. Use Render's load balancing features
2. Implement database connection pooling
3. Consider CDN for static content

## Backup and Recovery

### 1. Data Backup

**Google Sheets Backup**:
- Regular exports of plant data
- Version history in Google Sheets
- Consider automated backup scripts

### 2. Configuration Backup

**Environment Configuration**:
- Document all environment variables
- Store encrypted backups of service account keys
- Maintain deployment configuration versions

### 3. Disaster Recovery

**Recovery Plan**:
1. Redeploy from GitHub repository
2. Restore environment variables
3. Verify Google Sheets connectivity
4. Test all API endpoints

## Monitoring and Maintenance

### 1. Health Monitoring

**Automated Checks**:
```bash
# Health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://your-service.onrender.com/)
if [ $response != "200" ]; then
  echo "API health check failed: $response"
  # Send alert
fi
```

### 2. Log Analysis

**Key Metrics to Monitor**:
- API response times
- Error rates by endpoint
- Authentication failures
- Rate limit violations

### 3. Regular Maintenance

**Monthly Tasks**:
- Review and rotate API keys
- Update dependencies in `requirements.txt`
- Check Google Sheets API quotas
- Review access logs for anomalies

**Quarterly Tasks**:
- Performance optimization review
- Security audit
- Documentation updates
- Backup verification

## Support and Documentation

### Support Resources
- **Render.com Documentation**: [https://render.com/docs](https://render.com/docs)
- **Google Sheets API**: [https://developers.google.com/sheets/api](https://developers.google.com/sheets/api)
- **Flask Documentation**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)

### Additional Documentation
- **API Documentation**: `API_DOCUMENTATION.md`
- **ChatGPT Integration**: `CHATGPT_INTEGRATION.md`
- **Field Configuration**: `models/field_config.py`

---

*This deployment guide ensures a secure, scalable production deployment of the Plant Database API on render.com. Follow security best practices and monitor your deployment regularly.* 