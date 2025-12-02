# Redis Desktop Manager - No Keys Visible

## Quick Check: Is Redis Empty?

Run this command to test:

```powershell
uv run python test_redis_connection.py
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
1. Start your server: `uv run python app.py`
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

## How to View Keys in Redis Desktop Manager

### Method 1: Browse All Keys

1. **Click on your connection** in the left sidebar
2. **Expand the database** (usually "DB 0")
3. **Look for "Keys"** section
4. You should see all keys listed

### Method 2: Search for Job Keys

1. **Use the search box** (usually at the top)
2. **Type:** `job:*`
3. **Press Enter**
4. This will show all keys matching the pattern

### Method 3: Use Console/CLI

1. **Open Redis Console** in Redis Desktop Manager
2. **Run command:**
   ```
   KEYS job:*
   ```
3. This will list all job keys

---

## Create Test Data

If Redis is empty, create a test job:

### Option 1: Via API (Recommended)

1. **Start server:**
   ```powershell
   uv run python app.py
   ```

2. **Open browser:** `http://localhost:8000/docs`

3. **Upload a file:**
   - Expand `POST /api/v1/upload`
   - Click **"Try it out"**
   - Upload a test video/audio file
   - Fill in required fields
   - Click **"Execute"**

4. **Check Redis Desktop Manager** - you should now see a `job:*` key!

### Option 2: Via Command Line

```powershell
# Start server first
uv run python app.py

# In another terminal, use curl or Python to upload
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test.mp4" \
  -F "meeting_type=consultation" \
  -F "practice_area=employment_law" \
  -F "participants=Attorney John, Client Jane"
```

---

## Verify Redis Has Data

### Check via Command Line

```powershell
# Connect to Redis
redis-cli

# List all keys
KEYS *

# List job keys specifically
KEYS job:*

# Count keys
DBSIZE

# Get a specific job (replace with actual key)
HGETALL job:job_abc123_1234567890
```

### Check via Admin API

1. **Start server:** `uv run python app.py`
2. **Open:** `http://localhost:8000/api/v1/admin/stats`
3. **Look for:** `"total_jobs"` - should be > 0 if you have data

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
- ✅ Run `test_redis_connection.py` to verify
- ✅ Upload a test file via API

### Step 5: Search
- ✅ Use search box: type `job:*`
- ✅ Or use console: `KEYS job:*`

---

## Still Not Working?

### Check Redis is Actually Running

```powershell
redis-cli ping
```

Should return: `PONG`

### Check Connection Details

Make sure in Redis Desktop Manager:
- **Host:** `localhost` (not `127.0.0.1` - try both)
- **Port:** `6379`
- **Database:** `0`

### Check Your .env File

```env
REDIS_URL=redis://localhost:6379/0
```

### Try Different Redis Tool

If Redis Desktop Manager isn't working:
- Try **RedisInsight** (official tool)
- Try **Another Redis Desktop Manager**
- Use command line: `redis-cli`

---

## Quick Test Script

Run this to verify everything:

```powershell
uv run python test_redis_connection.py
```

This will:
- ✅ Test Redis connection
- 📊 Show how many keys exist
- 🔑 List all keys
- 📈 Show database info

---

## Expected Result

Once you have data, you should see keys like:

```
job:job_abc123def456_1234567890
job:job_xyz789ghi012_1234567891
```

Each key contains a hash with job data (status, filename, transcription, etc.)

