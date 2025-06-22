from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# === this script extracts lessons from the website , eg : mahara-tech===
cookie_string = """""" # extract your cookies and put them here 

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

cookies = convert_cookie_string_to_playwright(cookie_string)
course_url = "https://maharatech.gov.eg/course/view.php?id=2195"
output_file = "maven_all_lessons.txt"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    context.add_cookies(cookies)

    page = context.new_page()
    print("🌐 Visiting course page...")
    page.goto(course_url, timeout=60000)
    time.sleep(6)  # Wait for JS content

    soup = BeautifulSoup(page.content(), "html.parser")
    index_div = soup.select_one("#courseindex-content")

    if not index_div:
        print("❌ Sidebar not found. Login may have failed.")
        page.screenshot(path="sidebar_error.png")
        browser.close()
        exit()

    sections = index_div.select("div.courseindex-section")
    print(f"📦 Found {len(sections)} sections.")

    with open(output_file, "w", encoding="utf-8") as f:
        for sec in sections:
            title_tag = sec.select_one(".courseindex-section-title .courseindex-link")
            if not title_tag:
                continue

            section_title = title_tag.get_text(strip=True)
            section_url = title_tag["href"]
            print(f"\n📘 {section_title} ||| {section_url}")
            f.write(f"{section_title} ||| {section_url}\n")

            # Now grab all lessons under this section
            lessons = sec.select("li[id^=course-index-cm-] a.courseindex-link")
            for lesson in lessons:
                lesson_title = lesson.get_text(strip=True)
                lesson_url = lesson["href"]
                if "mod/hvp/view.php" in lesson_url:
                    print(f"   🎬 {lesson_title} → {lesson_url}")
                    f.write(f"\t{lesson_title} ||| {lesson_url}\n")

    print("\n✅ Done. All lessons written to:", output_file)
    page.screenshot(path="all_lessons_capture.png")
    browser.close()
