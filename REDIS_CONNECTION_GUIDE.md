# Redis Desktop Manager Connection Guide

## Quick Connection Details

**Default Local Redis Connection:**
- **Host:** `localhost` (or `127.0.0.1`)
- **Port:** `6379`
- **Database:** `0` (or leave empty)
- **Password:** (leave empty - no password by default)
- **Connection Name:** `AI Meeting Demo` (optional)

---

## Step-by-Step: Redis Desktop Manager

### 1. Open Redis Desktop Manager

Launch the application on your computer.

### 2. Add New Connection

- Click **"Connect to Redis Server"** or the **"+"** button
- Or go to **File → Add Connection**

### 3. Enter Connection Details

Fill in the connection form:

```
Name: AI Meeting Demo
Host: localhost
Port: 6379
Database: 0
Password: (leave empty)
```

**Advanced Settings (usually not needed):**
- **SSL/TLS:** Unchecked (unless you configured SSL)
- **SSH Tunnel:** Unchecked
- **Connection Timeout:** Default (5000ms)

### 4. Test Connection

- Click **"Test Connection"** button (if available)
- You should see: ✅ "Connection successful"

### 5. Connect

- Click **"Connect"** or **"Save"**
- Your Redis database should appear in the left sidebar

---

## If Connection Fails

### Check 1: Is Redis Running?

**Windows (PowerShell):**
```powershell
# Check if Redis is running
redis-cli ping
```

**Expected output:** `PONG`

If you get an error, Redis is not running. Start it:
- **WSL:** `sudo service redis-server start`
- **Memurai:** Check Windows Services
- **Docker:** `docker ps` (check if container is running)

### Check 2: Port 6379 Available?

```powershell
netstat -an | findstr 6379
```

You should see something like:
```
TCP    0.0.0.0:6379    0.0.0.0:0    LISTENING
```

### Check 3: Firewall Blocking?

Windows Firewall might be blocking Redis. Try:
1. Temporarily disable firewall
2. Test connection
3. If it works, add Redis to firewall exceptions

### Check 4: Check Your .env File

If you customized Redis settings, check your `.env` file:

```env
REDIS_URL=redis://localhost:6379/0
```

Or if you have a password:
```env
REDIS_URL=redis://:password@localhost:6379/0
```

---

## Alternative: Another Redis Desktop Manager

If you're using **Another Redis Desktop Manager**:

1. Click **"New Connection"**
2. Enter:
   - **Connection Name:** `AI Meeting Demo`
   - **Host:** `localhost`
   - **Port:** `6379`
   - **Database:** `0`
   - **Password:** (leave empty)
3. Click **"Connect"**

---

## Alternative: RedisInsight

If you're using **RedisInsight**:

1. Click **"Add Redis Database"**
2. Enter:
   - **Host:** `localhost`
   - **Port:** `6379`
   - **Database Alias:** `AI Meeting Demo`
   - **Username:** (leave empty)
   - **Password:** (leave empty)
3. Click **"Add Redis Database"**

---

## Viewing Your Data

Once connected, you should see:

### Keys Pattern
All job data is stored with the pattern: `job:*`

Examples:
- `job:job_abc123_1234567890`
- `job:job_def456_1234567891`

### Browse Jobs

1. In Redis Desktop Manager, look for keys starting with `job:`
2. Click on a key to view its contents
3. Jobs are stored as **Hash** data type

### Job Structure

Each job hash contains fields like:
- `job_id`
- `status` (queued, processing, completed, failed)
- `filename`
- `file_size_bytes`
- `created_at`
- `updated_at`
- `transcription` (JSON string)
- `summary` (JSON string)
- `progress`
- `current_step`

---

## Quick Test Commands

Once connected, you can run commands:

**In Redis Desktop Manager Console:**
```redis
# List all job keys
KEYS job:*

# Count total jobs
DBSIZE

# Get a specific job (replace with actual job_id)
HGETALL job:job_abc123_1234567890

# Get job status
HGET job:job_abc123_1234567890 status

# Check Redis info
INFO
```

---

## Troubleshooting

### "Connection refused" or "Cannot connect"

**Solution:**
1. Make sure Redis is running (see Check 1 above)
2. Verify port 6379 is correct
3. Check firewall settings

### "Authentication failed"

**Solution:**
- If you set a password, enter it in the connection form
- Check your `.env` file for `REDIS_URL` with password format:
  ```
  REDIS_URL=redis://:yourpassword@localhost:6379/0
  ```

### "Connection timeout"

**Solution:**
1. Increase timeout in connection settings
2. Check if Redis is actually running
3. Verify network connectivity

### Can't see any keys

**Solution:**
- Make sure you've uploaded at least one job
- Check you're connected to the correct database (usually `0`)
- Try: `KEYS *` to see all keys

---

## Need Help?

If you're still having issues:

1. **Check Redis is running:**
   ```powershell
   redis-cli ping
   ```

2. **Check your .env file** for custom Redis settings

3. **Try connecting via command line:**
   ```powershell
   redis-cli
   ```
   Then type: `PING` (should return `PONG`)

4. **Check Redis logs** (location depends on your installation)

---

## Connection String Format

If your tool asks for a connection string instead:

```
redis://localhost:6379/0
```

With password:
```
redis://:password@localhost:6379/0
```

With username and password:
```
redis://username:password@localhost:6379/0
```

---

## Next Steps

Once connected:
1. ✅ Browse your job keys (`job:*`)
2. ✅ View job details
3. ✅ Monitor Redis memory usage
4. ✅ Use the admin API endpoints for programmatic access

