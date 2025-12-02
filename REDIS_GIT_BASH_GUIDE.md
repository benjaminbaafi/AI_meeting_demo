# Redis Desktop Manager - Git Bash Guide

## Quick Check: Is Redis Empty?

Run this command in Git Bash:

```bash
uv run python test_redis_connection.py
```

Or if `uv run` doesn't work:

```bash
python test_redis_connection.py
```

This will tell you:
- ✅ If Redis is connected
- 📊 How many keys exist
- 🔑 What keys are in Redis

---

## Common Reasons You Don't See Keys

### 1. **No Jobs Created Yet** (Most Common)

If you haven't uploaded any videos/audio files yet, Redis will be empty!

**Solution:**
1. Start your server: `uv run python app.py` (or `python app.py`)
2. Go to `http://localhost:8000/docs`
3. Upload a test file via `POST /api/v1/upload`
4. Then check Redis Desktop Manager again

### 2. **Wrong Database Selected**

Redis has multiple databases (0-15). Make sure you're viewing database `0`.

**In Redis Desktop Manager:**
- Look for database selector (usually shows "DB 0" or "Database: 0")
- Make sure it's set to `0` (default)

### 3. **Need to Refresh**

**In Redis Desktop Manager:**
- Right-click → **Refresh** or press `F5`
- Or click the refresh button (🔄)

### 4. **Search/Filter Active**

Check if there's a search filter active:
- Clear any search/filter boxes
- Make sure you're viewing "All Keys" not a filtered view

---

## Git Bash Commands

### Test Redis Connection

```bash
# Test if Redis is running
redis-cli ping
```

Should return: `PONG`

### List All Keys

```bash
# Connect to Redis
redis-cli

# List all keys
KEYS *

# List job keys specifically
KEYS job:*

# Count keys
DBSIZE

# Exit Redis CLI
exit
```

### Check Redis Info

```bash
redis-cli INFO
```

---

## Create Test Data via Git Bash

### Option 1: Using curl

```bash
# Make sure server is running first!
# In another terminal: uv run python app.py

# Upload a test file
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test.mp4" \
  -F "meeting_type=consultation" \
  -F "practice_area=employment_law" \
  -F "participants=Attorney John, Client Jane"
```

### Option 2: Using Python Script

Create `upload_test.py`:

```python
import requests

files = {"file": open("test.mp4", "rb")}
data = {
    "meeting_type": "consultation",
    "practice_area": "employment_law",
    "participants": "Attorney John, Client Jane",
}

response = requests.post("http://localhost:8000/api/v1/upload", files=files, data=data)
print(response.json())
```

Run:
```bash
python upload_test.py
```

---

## Verify Redis Has Data

### Check via Git Bash

```bash
# Connect to Redis
redis-cli

# List all keys
KEYS *

# List job keys specifically  
KEYS job:*

# Count total keys
DBSIZE

# Get a specific job (replace with actual key)
HGETALL job:job_abc123_1234567890

# Exit
exit
```

### Check via Admin API

1. **Start server:** `uv run python app.py` (or `python app.py`)
2. **Open browser:** `http://localhost:8000/api/v1/admin/stats`
3. **Look for:** `"total_jobs"` - should be > 0 if you have data

Or use curl:

```bash
curl http://localhost:8000/api/v1/admin/stats
```

---

## Step-by-Step: View Keys in Redis Desktop Manager

### Step 1: Connect
- ✅ Make sure you're connected (green indicator)

### Step 2: Select Database
- ✅ Click on **"DB 0"** or **"Database 0"** in left sidebar

### Step 3: View Keys
- ✅ Click **"Keys"** folder or expand it
- ✅ You should see all keys listed

### Step 4: If Empty
- ✅ Check if you've created any jobs
- ✅ Run `python test_redis_connection.py` to verify
- ✅ Upload a test file via API

### Step 5: Search
- ✅ Use search box: type `job:*`
- ✅ Or use console: `KEYS job:*`

---

## Git Bash Scripts

### Quick Test Script

```bash
#!/bin/bash
# test_redis.sh

echo "Testing Redis connection..."

# Test Redis is running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running"
    echo "Start Redis first!"
    exit 1
fi

# Count keys
KEY_COUNT=$(redis-cli DBSIZE)
echo "📊 Total keys in database: $KEY_COUNT"

# List job keys
echo ""
echo "🔑 Job keys:"
redis-cli KEYS "job:*"

# List all keys (first 10)
echo ""
echo "📋 All keys (first 10):"
redis-cli KEYS "*" | head -10
```

Save as `test_redis.sh`, then:

```bash
chmod +x test_redis.sh
./test_redis.sh
```

---

## Troubleshooting in Git Bash

### Redis Command Not Found

If `redis-cli` doesn't work:

```bash
# Check if Redis is in PATH
which redis-cli

# If not found, add to PATH or use full path
# WSL: /usr/bin/redis-cli
# Windows: C:/path/to/redis-cli.exe
```

### Python Command Not Found

```bash
# Check Python
python --version
# or
python3 --version

# Check uv
uv --version
```

### Server Not Running

```bash
# Check if server is running on port 8000
curl http://localhost:8000/health

# Or check port
netstat -an | grep 8000
```

---

## Expected Result

Once you have data, you should see keys like:

```
job:job_abc123def456_1234567890
job:job_xyz789ghi012_1234567891
```

Each key contains a hash with job data (status, filename, transcription, etc.)

---

## Quick Commands Reference

```bash
# Test Redis
redis-cli ping

# List job keys
redis-cli KEYS "job:*"

# Count keys
redis-cli DBSIZE

# Get Redis info
redis-cli INFO

# Test API
curl http://localhost:8000/api/v1/admin/stats

# Test connection script
python test_redis_connection.py
```

---

## Still Not Working?

1. **Run test script:**
   ```bash
   python test_redis_connection.py
   ```

2. **Check Redis is running:**
   ```bash
   redis-cli ping
   ```

3. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Create a test job** via API docs or curl

5. **Refresh Redis Desktop Manager** (F5)

