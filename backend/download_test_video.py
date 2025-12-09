import os
import yt_dlp

def download_video():
    output_dir = "uploads"
    os.makedirs(output_dir, exist_ok=True)
    
    # Options for yt-dlp
    # We want a single file, preferably mp4, to be named 'mock_meeting.mp4'
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, 'mock_meeting.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'overwrites': True,
    }

    # Search query for a suitable mock meeting video
    # "ytsearch1:" tells yt-dlp to search and download the first result
    search_query = "ytsearch1:mock remote team meeting zoom"

    print(f"Searching and downloading video for: '{search_query}'...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        print("Download complete!")
    except Exception as e:
        print(f"Error downloading video: {e}")

if __name__ == "__main__":
    download_video()
