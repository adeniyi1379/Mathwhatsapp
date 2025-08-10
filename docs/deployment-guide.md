# SolveWithMe Platform Deployment Guide

## 🚀 Railway Deployment

### Prerequisites
- Railway account (railway.app)
- GitHub repository with your code
- Environment variables configured

### Step 1: Railway Setup

1. **Connect GitHub Repository**
   \`\`\`bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Link your project
   railway link
   \`\`\`

2. **Add Environment Variables**
   \`\`\`bash
   # Database (Railway PostgreSQL)
   railway add postgresql
   
   # Get database URL
   railway variables
   # Copy DATABASE_URL value
   \`\`\`

3. **Configure Environment Variables in Railway Dashboard**
   \`\`\`
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   TERMII_API_KEY=your_termii_key
   TERMII_SENDER_ID=SolveWithMe
   RETOOL_WEBHOOK_URL=your_retool_webhook
   ENABLE_SMS_NOTIFICATIONS=true
   ENABLE_VOICE_PROCESSING=true
   ENABLE_IMAGE_PROCESSING=true
   ENVIRONMENT=production
   \`\`\`

### Step 2: Database Initialization

1. **Run Database Scripts**
   \`\`\`bash
   # Connect to Railway PostgreSQL
   railway connect postgresql
   
   # Run in PostgreSQL shell:
   \i scripts/create_tables.sql
   \i scripts/seed_sample_data.sql
   \i scripts/add_analytics_tables.sql
   \`\`\`

2. **Verify Tables Created**
   \`\`\`sql
   \dt -- List all tables
   SELECT COUNT(*) FROM exam_questions; -- Should show sample questions
   \`\`\`

### Step 3: Deploy Application

1. **Deploy to Railway**
   \`\`\`bash
   # Deploy from current directory
   railway up
   
   # Or connect GitHub for auto-deploy
   railway connect # Select GitHub option
   \`\`\`

2. **Verify Deployment**
   \`\`\`bash
   # Check deployment status
   railway status
   
   # View logs
   railway logs
   
   # Get service URL
   railway domain
   \`\`\`

### Step 4: Configure Twilio Webhook

1. **Get your Railway URL**
   \`\`\`
   https://your-app-name.railway.app
   \`\`\`

2. **Configure Twilio Webhook**
   - Go to Twilio Console → WhatsApp → Sandbox
   - Set webhook URL: `https://your-app-name.railway.app/webhook/whatsapp`
   - Set HTTP method: `POST`

### Step 5: Test the Deployment

1. **Health Check**
   \`\`\`bash
   curl https://your-app-name.railway.app/health
   \`\`\`

2. **Send Test WhatsApp Message**
   - Send "Hello" to your Twilio WhatsApp number
   - Check Railway logs for processing

## 🔧 Supabase Integration (Alternative Database)

### If using Supabase instead of Railway PostgreSQL:

1. **Create Supabase Project**
   - Go to supabase.com
   - Create new project
   - Copy database URL

2. **Update Environment Variables**
   \`\`\`
   DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
   \`\`\`

3. **Run SQL Scripts in Supabase**
   - Go to Supabase → SQL Editor
   - Run each script file content

## 📊 Retool Dashboard Setup

### Step 1: Create Retool App

1. **Create New App**
   - Go to retool.com
   - Create new app: "SolveWithMe Analytics"

2. **Add Data Source**
   \`\`\`json
   {
     "type": "PostgreSQL",
     "host": "your-railway-postgres-host",
     "database": "railway",
     "username": "postgres",
     "password": "your-password"
   }
   \`\`\`

### Step 2: Create Webhook

1. **Add Webhook Component**
   - Add Webhook trigger
   - Copy webhook URL
   - Add to Railway environment variables

2. **Configure Webhook Handler**
   \`\`\`javascript
   // Webhook handler code
   const data = webhookBody.data;
   
   // Update charts with new data
   chart1.setData(data.platform_metrics);
   table1.setData(data.engagement_metrics);
   \`\`\`

## 🔐 Security Configuration

### Production Security Settings

1. **Environment Variables**
   \`\`\`bash
   # Never commit these to version control
   TWILIO_AUTH_TOKEN=keep_secret
   TERMII_API_KEY=keep_secret
   DATABASE_URL=keep_secret
   \`\`\`

2. **Railway Security**
   \`\`\`bash
   # Enable HTTPS (Railway does this automatically)
   # Configure CORS properly in main.py
   \`\`\`

3. **Database Security**
   \`\`\`sql
   -- Create read-only user for analytics
   CREATE USER analytics_user WITH PASSWORD 'secure_password';
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
   \`\`\`

## 📱 WhatsApp Business API (Production)

### For production scale, upgrade to WhatsApp Business API:

1. **Apply for WhatsApp Business API**
   - Go to developers.facebook.com
   - Apply for WhatsApp Business API access

2. **Configure Production Webhook**
   ```python
   # Update webhook endpoint for production
   @app.post("/webhook/whatsapp-business")
   async def whatsapp_business_webhook(request: Request):
       # Handle WhatsApp Business API webhooks
       pass
   \`\`\`

## 🔍 Monitoring Setup

### Step 1: Add Health Monitoring

1. **Configure Railway Monitoring**
   - Railway provides built-in monitoring
   - Set up alerts for downtime

2. **Add Custom Metrics**
   ```python
   # In main.py, add metrics endpoint
   @app.get("/metrics")
   async def get_metrics():
       return {
           "active_users": await get_active_user_count(),
           "questions_per_hour": await get_questions_per_hour(),
           "response_time": await get_avg_response_time()
       }
   \`\`\`

### Step 2: Error Tracking

1. **Add Sentry (Optional)**
   ```python
   # pip install sentry-sdk
   import sentry_sdk
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       traces_sample_rate=1.0
   )
   \`\`\`

## 📋 Pre-Launch Checklist

### ✅ Technical Checklist

- [ ] Database tables created and seeded
- [ ] All environment variables configured
- [ ] Twilio WhatsApp sandbox configured
- [ ] Termii SMS service tested
- [ ] Railway deployment successful
- [ ] Health check endpoint responding
- [ ] Retool dashboard connected
- [ ] Error logging configured

### ✅ Content Checklist

- [ ] WAEC/JAMB questions database populated
- [ ] Welcome messages in local languages
- [ ] Help documentation prepared
- [ ] Teacher onboarding materials ready

### ✅ Testing Checklist

- [ ] WhatsApp text messages working
- [ ] Image OCR processing tested
- [ ] Voice message transcription tested
- [ ] SMS notifications working
- [ ] Analytics data flowing to Retool
- [ ] Scheduled tasks running
- [ ] Database performance optimized

## 🎯 Go-Live Steps

### Day 1: Soft Launch
1. Deploy to production
2. Test with pilot schools (3 schools)
3. Monitor logs and performance
4. Gather initial feedback

### Week 1: Gradual Rollout
1. Add more schools gradually
2. Monitor system performance
3. Refine AI responses based on usage
4. Train teacher moderators

### Month 1: Full Launch
1. Open to all Nigerian secondary schools
2. Launch marketing campaign
3. Collect success stories
4. Plan feature enhancements

## 🔧 Troubleshooting

### Common Issues

1. **WhatsApp Messages Not Working**
   \`\`\`bash
   # Check Twilio webhook configuration
   curl -X POST https://your-app.railway.app/webhook/whatsapp \
     -H "Content-Type: application/json" \
     -d '{"from_number": "+2348012345678", "message_type": "text", "text": "test"}'
   \`\`\`

2. **Database Connection Issues**
   ```python
   # Test database connection
   async def test_db():
       try:
           async with db_service.pool.acquire() as conn:
               result = await conn.fetchval("SELECT 1")
               print(f"Database connected: {result}")
       except Exception as e:
           print(f"Database error: {e}")
   \`\`\`

3. **High Response Times**
   ```python
   # Add request timing middleware
   @app.middleware("http")
   async def add_process_time_header(request: Request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time
       response.headers["X-Process-Time"] = str(process_time)
       return response
   \`\`\`

## 📞 Support Contacts

- **Technical Issues**: tech@solvewithme.ng
- **School Partnerships**: schools@solvewithme.ng
- **General Support**: support@solvewithme.ng

---

**Next Steps**: After deployment, proceed with pilot school setup and teacher training materials.
\`\`\`

```python file="services/monitoring_service.py"
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
import httpx

logger = logging.getLogger(__name__)

class HealthMetrics:
    def __init__(self):
        self.cpu_percent = 0.0
        self.memory_percent = 0.0
        self.disk_percent = 0.0
        self.active_connections = 0
        self.response_times = []
        self.error_count = 0
        self.last_updated = datetime.utcnow()

class MonitoringService:
    def __init__(self, db_service):
        self.db_service = db_service
        self.health_metrics = HealthMetrics()
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 5000,
            'error_rate_percent': 10.0
        }
        
    async def collect_system_metrics(self):
        """Collect system health metrics"""
        try:
            # CPU usage
            self.health_metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.health_metrics.memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.health_metrics.disk_percent = (disk.used / disk.total) * 100
            
            # Update timestamp
            self.health_metrics.last_updated = datetime.utcnow()
            
            # Store in database
            await self._store_system_metrics()
            
            # Check for alerts
            await self._check_system_alerts()
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    async def _store_system_metrics(self):
        """Store system metrics in database"""
        if not self.db_service.pool:
            await self.db_service.init_pool()
        
        try:
            async with self.db_service.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO system_metrics (metric_name, metric_value, metric_unit) VALUES ($1, $2, $3)",
                    "cpu_percent", self.health_metrics.cpu_percent, "percent"
                )
                await conn.execute(
                    "INSERT INTO system_metrics (metric_name, metric_value, metric_unit) VALUES ($1, $2, $3)",
                    "memory_percent", self.health_metrics.memory_percent, "percent"
                )
                await conn.execute(
                    "INSERT INTO system_metrics (metric_name, metric_value, metric_unit) VALUES ($1, $2, $3)",
                    "disk_percent", self.health_metrics.disk_percent, "percent"
                )
        except Exception as e:
            logger.error(f"Error storing system metrics: {str(e)}")
    
    async def _check_system_alerts(self):
        """Check if system metrics exceed alert thresholds"""
        alerts = []
        
        if self.health_metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {self.health_metrics.cpu_percent:.1f}%")
        
        if self.health_metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {self.health_metrics.memory_percent:.1f}%")
        
        if self.health_metrics.disk_percent > self.alert_thresholds['disk_percent']:
            alerts.append(f"High disk usage: {self.health_metrics.disk_percent:.1f}%")
        
        if alerts:
            await self._send_system_alert(alerts)
    
    async def _send_system_alert(self, alerts: List[str]):
        """Send system alert notifications"""
        alert_message = "🚨 System Alert - SolveWithMe Platform\n\n"
        alert_message += "\n".join(alerts)
        alert_message += f"\n\nTime: {datetime.utcnow().isoformat()}"
        alert_message += "\n\nPlease check system resources immediately."
        
        # Log the alert
        logger.error(f"System alert triggered: {alerts}")
        
        # In production, you would send this to admin team
        # via email, Slack, or other notification service
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            "status": "healthy" if self._is_system_healthy() else "degraded",
            "timestamp": self.health_metrics.last_updated.isoformat(),
            "metrics": {
                "cpu_percent": self.health_metrics.cpu_percent,
                "memory_percent": self.health_metrics.memory_percent,
                "disk_percent": self.health_metrics.disk_percent,
                "active_connections": self.health_metrics.active_connections
            },
            "thresholds": self.alert_thresholds
        }
    
    def _is_system_healthy(self) -> bool:
        """Check if system is healthy based on metrics"""
        return (
            self.health_metrics.cpu_percent < self.alert_thresholds['cpu_percent'] and
            self.health_metrics.memory_percent < self.alert_thresholds['memory_percent'] and
            self.health_metrics.disk_percent < self.alert_thresholds['disk_percent']
        )
    
    async def track_response_time(self, endpoint: str, response_time_ms: float):
        """Track API response times"""
        self.health_metrics.response_times.append({
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only last 100 response times
        if len(self.health_metrics.response_times) > 100:
            self.health_metrics.response_times = self.health_metrics.response_times[-100:]
        
        # Check for slow responses
        if response_time_ms > self.alert_thresholds['response_time_ms']:
            logger.warning(f"Slow response detected: {endpoint} took {response_time_ms}ms")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.health_metrics.response_times:
            return {"average_response_time": 0, "slow_requests": 0}
        
        response_times = [r['response_time_ms'] for r in self.health_metrics.response_times]
        avg_response_time = sum(response_times) / len(response_times)
        slow_requests = len([r for r in response_times if r > self.alert_thresholds['response_time_ms']])
        
        return {
            "average_response_time_ms": round(avg_response_time, 2),
            "slow_requests": slow_requests,
            "total_requests": len(response_times),
            "p95_response_time": round(sorted(response_times)[int(len(response_times) * 0.95)], 2) if response_times else 0
        }
    
    async def check_external_services(self) -> Dict[str, bool]:
        """Check health of external services"""
        services_status = {}
        
        # Check Twilio API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.twilio.com/", timeout=10.0)
                services_status['twilio'] = response.status_code == 200
        except:
            services_status['twilio'] = False
        
        # Check Termii API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.ng.termii.com/", timeout=10.0)
                services_status['termii'] = response.status_code == 200
        except:
            services_status['termii'] = False
        
        return services_status
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        if not self.db_service.pool:
            return {"status": "disconnected"}
        
        try:
            async with self.db_service.pool.acquire() as conn:
                # Get connection info
                connection_info = await conn.fetchrow("SELECT count(*) as connections FROM pg_stat_activity")
                
                # Get database size
                db_size = await conn.fetchrow("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
                
                # Get table sizes
                table_sizes = await conn.fetch("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 5
                """)
                
                return {
                    "status": "connected",
                    "active_connections": connection_info['connections'],
                    "database_size": db_size['size'],
                    "largest_tables": [
                        {"table": f"{row['schemaname']}.{row['tablename']}", "size": row['size']}
                        for row in table_sizes
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting database metrics: {str(e)}")
            return {"status": "error", "error": str(e)}

# Background task to collect metrics periodically
async def start_monitoring_loop(monitoring_service: MonitoringService):
    """Start background monitoring loop"""
    while True:
        try:
            await monitoring_service.collect_system_metrics()
            await asyncio.sleep(60)  # Collect metrics every minute
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
            await asyncio.sleep(60)
