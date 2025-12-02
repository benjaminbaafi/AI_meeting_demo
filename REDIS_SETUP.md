# Redis Setup Guide for Windows

This guide will help you install and run Redis locally on Windows for the AI Meeting Participant project.

## Option 1: Using WSL (Windows Subsystem for Linux) - Recommended

### 1. Install WSL (if not already installed)

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Restart your computer when prompted.

### 2. Install Redis in WSL

After restart, open Ubuntu (or your WSL distribution) and run:

```bash
sudo apt update
sudo apt install redis-server -y
```

### 3. Start Redis

```bash
sudo service redis-server start
```

### 4. Verify Redis is running

```bash
redis-cli ping
```

You should see `PONG` as the response.

### 5. Configure Redis to start automatically

```bash
sudo systemctl enable redis-server
```

### 6. Update your .env file

Add or update in your `.env` file:

```env
REDIS_URL=redis://localhost:6379/0
```

**Note:** Redis running in WSL is accessible from Windows at `localhost:6379`.

---

## Option 2: Using Memurai (Windows Native Redis)

Memurai is a Redis-compatible server for Windows.

### 1. Download Memurai

Download from: https://www.memurai.com/get-memurai

### 2. Install Memurai

Run the installer and follow the setup wizard. It will install Memurai as a Windows service.

### 3. Verify Installation

Open PowerShell and test:

```powershell
memurai-cli ping
```

You should see `PONG`.

### 4. Update your .env file

```env
REDIS_URL=redis://localhost:6379/0
```

---

## Option 3: Using Docker (if you have Docker Desktop)

### 1. Pull Redis image

```powershell
docker pull redis:latest
```

### 2. Run Redis container

```powershell
docker run -d -p 6379:6379 --name redis-server redis:latest
```

### 3. Verify Redis is running

```powershell
docker ps
```

You should see `redis-server` in the list.

### 4. Update your .env file

```env
REDIS_URL=redis://localhost:6379/0
```

---

## Option 4: Using Chocolatey

### 1. Install Redis via Chocolatey

Open PowerShell as Administrator:

```powershell
choco install redis-64 -y
```

### 2. Start Redis service

```powershell
redis-server
```

Or install as a Windows service:

```powershell
redis-server --service-install
redis-server --service-start
```

### 3. Update your .env file

```env
REDIS_URL=redis://localhost:6379/0
```

---

## Verify Redis Connection

After installation, test the connection:

### Using Python

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # Should print: True
```

### Using redis-cli

```bash
redis-cli ping
# Should output: PONG
```

---

## Configuration

The default Redis configuration in `config.py`:

- **Redis URL**: `redis://localhost:6379/0` (default)
- **Max Connections**: 10
- **Job TTL**: 7 days (604800 seconds)

You can override these in your `.env` file:

```env
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10
REDIS_JOB_TTL_SECONDS=604800
```

---

## Troubleshooting

### Redis connection refused

1. Check if Redis is running:
   ```powershell
   redis-cli ping
   ```

2. Check if port 6379 is in use:
   ```powershell
   netstat -an | findstr 6379
   ```

3. Verify your `.env` file has the correct `REDIS_URL`

### Redis module not found

Install the Python Redis package:

```powershell
uv pip install redis>=5.0.0
```

### Connection timeout

- Make sure Redis is running
- Check firewall settings
- Verify `REDIS_URL` in `.env` matches your Redis installation

---

## Next Steps

1. ✅ Install Redis using one of the methods above
2. ✅ Update your `.env` file with `REDIS_URL`
3. ✅ Install Python dependencies: `uv pip install -r requirements.txt`
4. ✅ Start your application: `uv run python app.py`

Your jobs will now be persisted in Redis instead of in-memory storage!

