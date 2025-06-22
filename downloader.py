import yt_dlp


# this one is for downloading youtube videos 

input_file = "youtube_links_maven.txt"
download_dir = "maven_course"

# yt-dlp options
ydl_opts = {
    'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
    'format': 'best',
    'quiet': False,
    'noplaylist': True,
    'merge_output_format': 'mp4'
}

# Read YouTube links from file
with open(input_file, "r", encoding="utf-8") as f:
    video_entries = [line.strip().split(" ||| ") for line in f if "youtube.com" in line and "NOT_FOUND" not in line and "ERROR" not in line]

print(f"🎯 Found {len(video_entries)} videos to download.")

# Download each video
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for title, url in video_entries:
        print(f"\n⬇️ Downloading: {title}")
        try:
            ydl.download([url])
        except Exception as e:
            print(f"❌ Failed to download {title}: {e}")
