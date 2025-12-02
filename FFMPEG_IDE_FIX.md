# Fix FFmpeg Not Detected in IDE Terminal

If FFmpeg works in your regular terminal but not in your IDE terminal, here's how to fix it:

## Quick Fixes

### Option 1: Restart Your IDE
The IDE terminal may not have picked up the updated PATH. Simply restart your IDE (Cursor/VS Code/etc.) and try again.

### Option 2: Find FFmpeg Path and Add to .env

1. **Find where FFmpeg is installed:**

   In your regular terminal (where FFmpeg works), run:
   ```powershell
   where.exe ffmpeg
   ```
   
   This will show something like:
   ```
   C:\ffmpeg\bin\ffmpeg.exe
   ```

2. **Add to your `.env` file:**

   Open `.env` in your project root and add:
   ```env
   FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
   ```
   
   (Replace with your actual path from step 1)

3. **Restart your application**

### Option 3: Refresh IDE Terminal PATH

**For VS Code / Cursor:**

1. Close all terminal windows in the IDE
2. Open a new terminal
3. Run:
   ```powershell
   $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   ```
4. Test:
   ```powershell
   ffmpeg -version
   ```

### Option 4: Add FFmpeg to User PATH (Permanent Fix)

1. **Find FFmpeg location:**
   ```powershell
   where.exe ffmpeg
   ```

2. **Add to User PATH:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to **Advanced** tab → **Environment Variables**
   - Under **User variables**, select `Path` → **Edit**
   - Click **New** → Add the folder containing `ffmpeg.exe` (e.g., `C:\ffmpeg\bin`)
   - Click **OK** on all dialogs

3. **Restart your IDE**

### Option 5: Use Full Path in Code (Temporary)

If you need a quick workaround, you can temporarily hardcode the path in `config.py`:

```python
ffmpeg_path: Optional[str] = Field(default=r"C:\ffmpeg\bin\ffmpeg.exe")
```

But **Option 2** (using `.env`) is better for production.

## Verify Fix

After applying any fix, test in your IDE terminal:

```powershell
ffmpeg -version
```

You should see FFmpeg version information.

## Why This Happens

- IDE terminals sometimes don't inherit the full system PATH
- PATH changes require IDE restart to take effect
- Some IDEs cache environment variables

## Still Not Working?

1. Check if FFmpeg is actually in PATH:
   ```powershell
   $env:Path -split ';' | Select-String -Pattern 'ffmpeg'
   ```

2. Verify FFmpeg executable exists:
   ```powershell
   Test-Path "C:\ffmpeg\bin\ffmpeg.exe"
   ```
   (Replace with your actual path)

3. Try the `.env` method (Option 2) - it's the most reliable!

