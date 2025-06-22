from playwright.sync_api import sync_playwright
import time
import re


## this is for extracting youtube links from actual lessons  

# === Your session cookies copied from browser ===
cookie_string = """""" # your cookies here 
def convert_cookie_string_to_playwright(cookie_str):
    cookies = []
    for pair in cookie_str.split(";"):
        if "=" not in pair:
            continue
        name, value = pair.strip().split("=", 1)
        cookies.append({
            "name": name,
            "value": value,
            "domain": "maharatech.gov.eg",
            "path": "/",
            "httpOnly": False,
            "secure": False,
            "sameSite": "Lax"
        })
    return cookies

# === Extract clean YouTube URL from embed link ===
def clean_youtube_url(iframe_url):
    match = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", iframe_url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    return iframe_url  # fallback to original if pattern not found

cookies = convert_cookie_string_to_playwright(cookie_string)

# === Load lesson links ===
with open("maven_course_chapters.txt", "r", encoding="utf-8") as f:
    lesson_links = [line.strip().split(" ||| ") for line in f if "mod/hvp/view.php" in line]

# === Playwright session ===
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    context.add_cookies(cookies)

    page = context.new_page()

    with open("youtube_links_maven.txt", "w", encoding="utf-8") as out:
        for title, url in lesson_links:
            print(f"\n🌐 Visiting: {title}")

            # 🚿 Clear previous page DOM to avoid iframe duplication issues
            page.goto("about:blank")
            time.sleep(2)

            try:
                page.goto(url, timeout=120000)
                time.sleep(8)  # Let iframe load

                yt_url = None

                for attempt in range(5):
                    print(f"⏳ Attempt {attempt + 1}: checking for iframe...")
                    page.evaluate("window.scrollBy(0, 9999)")  # scroll down to force JS render
                    time.sleep(3)

                    for frame in page.frames:
                        if "youtube.com" in frame.url:
                            print(f"🔍 Frame found: {frame.url}")
                            yt_url = frame.url
                            break

                    if yt_url:
                        break

                # ✅ Clean the URL
                if yt_url and "/embed/" in yt_url:
                    video_id = yt_url.split("/embed/")[1].split("?")[0]
                    yt_url = f"https://www.youtube.com/watch?v={video_id}"

                if yt_url:
                    print(f"🎬 Cleaned YouTube: {yt_url}")
                    out.write(f"{title} ||| {yt_url}\n")
                else:
                    print(f"❌ No YouTube link found for: {title}")
                    out.write(f"{title} ||| NOT_FOUND\n")

            except Exception as e:
                print(f"💥 Error on {title}: {e}")
                out.write(f"{title} ||| ERROR\n")

    browser.close()