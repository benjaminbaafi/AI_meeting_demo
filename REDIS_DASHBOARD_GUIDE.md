# Redis Dashboard Guide

This guide shows you how to view and manage your Redis database for the AI Meeting Participant system.

## Option 1: Built-in Admin API Endpoints (Recommended)

We've created admin endpoints that you can access via the FastAPI docs interface.

### Access Admin Endpoints

1. **Start your server:**
   ```powershell
   uv run python app.py
   ```

2. **Open FastAPI docs:**
   - Go to: `http://localhost:8000/docs`
   - Look for the **"Admin"** section

### Available Admin Endpoints

#### 1. List All Jobs
- **GET** `/api/v1/admin/jobs`
- **Query Parameters:**
  - `status` (optional): Filter by status (queued, processing, completed, failed)
  - `limit` (default: 100): Maximum number of jobs to return
  - `offset` (default: 0): Pagination offset
- **Example:** `http://localhost:8000/api/v1/admin/jobs?status=completed&limit=50`

#### 2. Get Job Details
- **GET** `/api/v1/admin/jobs/{job_id}`
- Returns full job data including transcription and summary

#### 3. Get Redis Statistics
- **GET** `/api/v1/admin/stats`
- Returns:
  - Total number of jobs
  - Jobs by status
  - Redis memory usage
  - Server information

#### 4. Delete Job
- **DELETE** `/api/v1/admin/jobs/{job_id}`
- Permanently removes a job from Redis

#### 5. List Redis Keys
- **GET** `/api/v1/admin/redis/keys`
- **Query Parameters:**
  - `pattern` (default: "job:*"): Key pattern to search
  - `limit` (default: 100): Maximum keys to return
- Useful for debugging

### Using the Admin API

**Via Browser (FastAPI Docs):**
1. Go to `http://localhost:8000/docs`
2. Expand the **Admin** section
3. Click **Try it out** on any endpoint
4. Fill in parameters and click **Execute**

**Via curl:**
```powershell
# List all jobs
curl http://localhost:8000/api/v1/admin/jobs

# Get stats
curl http://localhost:8000/api/v1/admin/stats

# Get specific job
curl http://localhost:8000/api/v1/admin/jobs/job_abc123
```

**Via Python:**
```python
import requests

# List jobs
response = requests.get("http://localhost:8000/api/v1/admin/jobs")
print(response.json())

# Get stats
stats = requests.get("http://localhost:8000/api/v1/admin/stats")
print(stats.json())
```

---

## Option 2: External Redis GUI Tools

### RedisInsight (Official Redis GUI) - Recommended

**Download:**
- Windows: https://redis.com/redis-enterprise/redis-insight/
- Free and official Redis management tool

**Setup:**
1. Download and install RedisInsight
2. Open RedisInsight
3. Click **"Add Redis Database"**
4. Enter connection details:
   - **Host:** `localhost`
   - **Port:** `6379`
   - **Database Alias:** `AI Meeting Demo`
5. Click **"Add Redis Database"**

**Features:**
- Browse all keys
- View job data in JSON format
- Search and filter keys
- Monitor Redis performance
- Execute Redis commands

### Redis Commander (Web-based)

**Install:**
```powershell
npm install -g redis-commander
```

**Run:**
```powershell
redis-commander
```

**Access:**
- Open browser: `http://localhost:8081`
- Automatically connects to localhost:6379

### Another Redis Desktop Manager (Another Redis Desktop Manager)

**Download:**
- https://github.com/qishibo/AnotherRedisDesktopManager/releases
- Free, open-source Redis GUI

**Setup:**
1. Download and install
2. Click **"New Connection"**
3. Enter:
   - **Host:** `localhost`
   - **Port:** `6379`
4. Click **"Connect"**

---

## Option 3: Command Line (redis-cli)

If you have Redis installed, you can use the command line:

### Basic Commands

```bash
# Connect to Redis
redis-cli

# List all job keys
KEYS job:*

# Get a specific job
HGETALL job:job_abc123

# Count jobs
DBSIZE

# Get Redis info
INFO

# Monitor Redis commands in real-time
MONITOR
```

### Useful Redis CLI Commands

```bash
# Scan for job keys (safer than KEYS for production)
SCAN 0 MATCH job:* COUNT 100

# Get all fields of a job hash
HGETALL job:job_abc123

# Get specific field
HGET job:job_abc123 status

# Delete a job
DEL job:job_abc123

# Check if key exists
EXISTS job:job_abc123

# Get TTL (time to live)
TTL job:job_abc123
```

---

## Option 4: Create a Simple HTML Dashboard

You can create a simple HTML dashboard that uses the admin API endpoints.

**Create `dashboard.html` in your project root:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Redis Dashboard - AI Meeting Participant</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-box { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Redis Dashboard</h1>
    
    <div class="stats" id="stats"></div>
    
    <h2>Jobs</h2>
    <table id="jobs-table">
        <thead>
            <tr>
                <th>Job ID</th>
                <th>Status</th>
                <th>Filename</th>
                <th>Created</th>
                <th>Progress</th>
            </tr>
        </thead>
        <tbody id="jobs-body"></tbody>
    </table>
    
    <script>
        const API_URL = 'http://localhost:8000/api/v1/admin';
        
        async function loadStats() {
            const response = await fetch(`${API_URL}/stats`);
            const stats = await response.json();
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-box">
                    <h3>Total Jobs</h3>
                    <p>${stats.total_jobs}</p>
                </div>
                <div class="stat-box">
                    <h3>Completed</h3>
                    <p>${stats.jobs_by_status.completed || 0}</p>
                </div>
                <div class="stat-box">
                    <h3>Processing</h3>
                    <p>${stats.jobs_by_status.processing || 0}</p>
                </div>
                <div class="stat-box">
                    <h3>Memory</h3>
                    <p>${stats.used_memory_human}</p>
                </div>
            `;
        }
        
        async function loadJobs() {
            const response = await fetch(`${API_URL}/jobs?limit=100`);
            const data = await response.json();
            
            const tbody = document.getElementById('jobs-body');
            tbody.innerHTML = data.jobs.map(job => `
                <tr>
                    <td><a href="${API_URL}/jobs/${job.job_id}">${job.job_id}</a></td>
                    <td>${job.status}</td>
                    <td>${job.filename || 'N/A'}</td>
                    <td>${job.created_at || 'N/A'}</td>
                    <td>${job.progress || 0}%</td>
                </tr>
            `).join('');
        }
        
        loadStats();
        loadJobs();
        
        // Refresh every 5 seconds
        setInterval(() => {
            loadStats();
            loadJobs();
        }, 5000);
    </script>
</body>
</html>
```

**Access:**
- Open `dashboard.html` in your browser
- Make sure your API server is running on `http://localhost:8000`

---

## Recommended Approach

**For Development:**
- Use the **FastAPI docs** (`/docs`) - it's built-in and easy to use
- Or use **RedisInsight** for a visual interface

**For Production:**
- Use the **Admin API endpoints** programmatically
- Or create a custom dashboard using the admin API
- Consider adding authentication to admin endpoints

---

## Security Note

⚠️ **Important:** The admin endpoints are currently **not protected**. In production, you should:

1. Add authentication (API keys, JWT tokens, etc.)
2. Restrict access to admin endpoints
3. Use environment-based access control

Example protection:
```python
from fastapi import Depends, HTTPException, Header

async def verify_admin_token(x_admin-token: str = Header(...)):
    if x_admin-token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

@router.get("/admin/jobs", dependencies=[Depends(verify_admin_token)])
async def list_all_jobs(...):
    ...
```

---

## Next Steps

1. ✅ Start your server: `uv run python app.py`
2. ✅ Visit `http://localhost:8000/docs` → Admin section
3. ✅ Try the `/api/v1/admin/stats` endpoint
4. ✅ List jobs with `/api/v1/admin/jobs`
5. 🔄 Optionally install RedisInsight for a visual interface

