# Production Setup Guide

## Overview
This document outlines the production deployment requirements for the Plant Database API.

## Environment Variables

### Required
- `GARDENLLM_API_KEY`: Your API key for write operations

### Optional (Production Recommended)
- `REDIS_URL`: Redis connection URL for production-grade rate limiting
  - Format: `redis://[user:password@]host:port[/database]`
  - Example: `redis://localhost:6379/0`
  - If not set, API will use in-memory rate limiting (not recommended for production)

## Rate Limiting Storage

### Production (Recommended)
- **Redis**: Provides persistent, scalable rate limiting across server restarts
- **Benefits**: 
  - Survives server restarts
  - Shared across multiple API instances
  - Better performance under load
- **Setup**: Set `REDIS_URL` environment variable

### Development/Fallback
- **In-Memory**: Simple storage that resets on server restart
- **When used**: 
  - During testing (automatically enabled)
  - When `REDIS_URL` is not configured
  - When Redis connection fails (automatic fallback)

## Render.com Deployment

### Adding Redis to Render
1. Go to your Render dashboard
2. Create a new **Redis** service
3. Copy the **Internal Redis URL** 
4. In your web service, add environment variable:
   - Key: `REDIS_URL`
   - Value: [Your Redis Internal URL]

### Alternative Redis Providers
- **Upstash Redis**: Free tier available
- **Redis Cloud**: Managed Redis service
- **Railway**: Simple Redis deployment

## Dependencies Updated
The following deprecated modules have been removed:
- `Deprecated==1.2.18`
- `typing-inspection==0.4.1`
- `pytz==2025.2`
- Various unused dependencies

## Monitoring
- Rate limit breaches are logged with WARNING level
- Redis connection status is logged during startup
- Check logs for `"Rate limiting configured with Redis storage"` message

## Troubleshooting

### Rate Limiting Warnings
```
Using the in-memory storage for tracking rate limits...
```
**Solution**: Set `REDIS_URL` environment variable

### Redis Connection Failed
```
Redis connection failed, falling back to in-memory storage
```
**Solution**: Check Redis URL format and Redis service availability 