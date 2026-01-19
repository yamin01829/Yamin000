import urllib.request
from bs4 import BeautifulSoup
import ssl
import time
import os
from urllib.parse import urlparse
import sys

ssl._create_default_https_context = ssl._create_unverified_context

HEADERS = {
'User-Agent': 'Mozilla/5.0 (Android 10; Mobile)'
}

ক্যাটাগরি এবং তাদের লিংক

CATEGORIES = {
"Bangla_Movie": "https://www.notunmovie.link/category/bangla-movie/",
"Bangla_Natok": "https://www.notunmovie.link/category/bangla-natok/",
"Bangla_Web_Series": "https://www.notunmovie.link/category/bangla-web-series/",
"Kolkata_Movie": "https://www.notunmovie.link/tag/kolkata-movie/",
"Bangla_Dubbing_Movie": "https://www.notunmovie.link/category/bangla-dubbing-movie/",
"Bangla_Dubbing_Web_Series": "https://www.notunmovie.link/category/bangla-dubbing-web-series/",
"Hindi_Movie": "https://www.notunmovie.link/category/hindi-movie/",
"Hindi_Dubbed_Movie": "https://www.notunmovie.link/category/hindi-dubbed-movie/",
"Hindi_Web_Series": "https://www.notunmovie.link/category/hindi-web-series/",
"Bangla Hot Web Series Collection (18+)": "https://www.notunmovie.link/category/bangla-hot-web-series-collection/"
}

def read_existing_links(filename):
"""ফাইল থেকে বিদ্যমান লিংক পড়ে আসে"""
if not os.path.exists(filename):
return set()

with open(filename, "r", encoding="utf-8") as f:  
    links = set()  
    for line in f:  
        line = line.strip()  
        # শুধুমাত্র লিংক লাইন নিবে (কমেন্ট বা হেডার নয়)  
        if line and not line.startswith('#') and not line.startswith('=') and '://' in line:  
            links.add(line)  
return links

def scrape_category(category_name, base_url):
"""একটি নির্দিষ্ট ক্যাটাগরি স্ক্র্যাপ করে"""
print(f"\n{'='*60}")
print(f"🎬 {category_name} স্ক্র্যাপিং শুরু...")
print(f"🔗 URL: {base_url}")
print(f"{'='*60}")

# শুভ ফোল্ডারের ভিতরে ফাইল সেভ হবে  
if not os.path.exists("shuvo"):  
    os.makedirs("shuvo")  
  
filename = f"shuvo/{category_name}.txt"  
existing_links = read_existing_links(filename)  
all_links = existing_links.copy()  
new_links = set()  
  
page = 1  
empty_pages = 0  
max_empty_pages = 2  # 2টি খালি পেজ পাওয়ার পর থামবে  
  
while True:  
    try:  
        # URL তৈরি  
        if page == 1:  
            url = base_url.rstrip('/') + "/"  
        else:  
            url = f"{base_url.rstrip('/')}/page/{page}/"  
          
        print(f"📄 {category_name} - Page {page} স্ক্যান করা হচ্ছে...")  
          
        # রিকুয়েস্ট পাঠানো  
        req = urllib.request.Request(url, headers=HEADERS)  
        response = urllib.request.urlopen(req, timeout=30)  
          
        # HTTP স্ট্যাটাস চেক  
        if response.status != 200:  
            print(f"⚠️  Page {page}: HTTP Status {response.status}")  
            break  
          
        html = response.read()  
        soup = BeautifulSoup(html, 'html.parser')  
          
        found_this_page = 0  
          
        # প্রথমে h2, h3 ট্যাগে লিংক খুঁজি  
        for h in soup.find_all(['h2', 'h3']):  
            a = h.find('a')  
            if a and a.get('href'):  
                link = a['href'].strip()  
                if link and '://' in link:  
                    # ডুপ্লিকেট চেক  
                    if link not in all_links and link not in new_links:  
                        # একই ডোমেইন চেক  
                        if 'notunmovie.link' in link or 'movie' in link.lower() or 'natok' in link.lower():  
                            new_links.add(link)  
                            all_links.add(link)  
                            found_this_page += 1  
                            print(f"   ✅ নতুন লিংক #{len(new_links):03d}")  
          
        # তারপর article ট্যাগ চেক  
        for article in soup.find_all('article'):  
            a = article.find('a')  
            if a and a.get('href'):  
                link = a['href'].strip()  
                if link and '://' in link:  
                    if link not in all_links and link not in new_links:  
                        if 'notunmovie.link' in link or 'movie' in link.lower() or 'natok' in link.lower():  
                            new_links.add(link)  
                            all_links.add(link)  
                            found_this_page += 1  
                            print(f"   ✅ নতুন লিংক #{len(new_links):03d}")  
          
        # তারপর সব a ট্যাগ চেক  
        if found_this_page == 0:  
            for a in soup.find_all('a', href=True):  
                link = a['href'].strip()  
                if link and '://' in link:  
                    if link not in all_links and link not in new_links:  
                        if 'notunmovie.link' in link or 'movie' in link.lower() or 'natok' in link.lower() or 'series' in link.lower():  
                            new_links.add(link)  
                            all_links.add(link)  
                            found_this_page += 1  
                            print(f"   ✅ নতুন লিংক #{len(new_links):03d}")  
          
        # খালি পেজ কাউন্ট  
        if found_this_page == 0:  
            empty_pages += 1  
            print(f"   ℹ️  এই পেজে নতুন লিংক পাওয়া যায়নি ({empty_pages}/{max_empty_pages})")  
              
            if empty_pages >= max_empty_pages:  
                print(f"\n⛔ {category_name} - {max_empty_pages}টি খালি পেজ পাওয়ায় স্ক্র্যাপিং বন্ধ")  
                break  
        else:  
            empty_pages = 0  # নতুন লিংক পাওয়ায় রিসেট  
          
        # সামান্য বিরতি দেই  
        time.sleep(0.5)  
        page += 1  
          
    except urllib.error.HTTPError as e:  
        if e.code == 404:  
            print(f"\n⛔ {category_name} - Page {page} পাওয়া যায়নি (404)")  
            break  
        else:  
            print(f"\n⚠️  HTTP Error {e.code}: {e.reason}")  
            break  
              
    except urllib.error.URLError as e:  
        print(f"\n⚠️  URL Error: {e.reason}")  
        break  
          
    except Exception as e:  
        print(f"\n❌ Error: {str(e)}")  
        break  
  
# নতুন লিংক সেভ করা  
if new_links:  
    # আগের সব লিংক পড়ে নিই  
    all_existing_links = list(read_existing_links(filename))  
      
    # নতুন ফাইল তৈরি করি  
    with open(filename, "w", encoding="utf-8") as f:  
        # হেডার লিখি  
        f.write(f"{'='*60}\n")  
        f.write(f"# {category_name}\n")  
        f.write(f"# স্ক্র্যাপিং তারিখ: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")  
        f.write(f"# মোট লিংক: {len(all_existing_links) + len(new_links)}\n")  
        f.write(f"{'='*60}\n\n")  
          
        # আগের লিংকগুলো লিখি  
        for link in sorted(all_existing_links):  
            f.write(link + "\n")  
          
        # নতুন লিংকগুলো লিখি  
        for link in sorted(new_links):  
            f.write(link + "\n")  
      
    print(f"\n💾 {category_name}: {len(new_links)} টি নতুন লিংক যোগ করা হয়েছে")  
    print(f"📊 মোট লিংক: {len(all_existing_links) + len(new_links)} → {filename}")  
else:  
    print(f"\n📭 {category_name}: কোন নতুন লিংক পাওয়া যায়নি")  
    print(f"📊 পূর্বের লিংক: {len(existing_links)} → {filename}")  
  
print(f"{'='*60}")  
return len(new_links)

def main():
"""মেইন ফাংশন - সবকিছু অটোমেটিক চালাবে"""
print("\n" + "="*60)
print("🚀 নতুন মুভি অটোমেটিক স্ক্র্যাপার")
print("="*60)
print(f"⏰ শুরু: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📁 মোট ক্যাটাগরি: {len(CATEGORIES)}")
print("="*60)

# শুভ ফোল্ডার তৈরি  
if not os.path.exists("shuvo"):  
    os.makedirs("shuvo")  
    print("📂 'shuvo' ফোল্ডার তৈরি করা হয়েছে")  
  
total_new_links = 0  
category_count = 1  
  
for category_name, base_url in CATEGORIES.items():  
    print(f"\n[{category_count}/{len(CATEGORIES)}]", end=" ")  
    new_links_count = scrape_category(category_name, base_url)  
    total_new_links += new_links_count  
    category_count += 1  
      
    # প্রতি ক্যাটাগরি পর সামান্য বিরতি  
    if category_count <= len(CATEGORIES):  
        print(f"\n⏳ পরবর্তী ক্যাটাগরির জন্য প্রস্তুত হচ্ছি...")  
        time.sleep(2)  
  
# ফাইনাল রিপোর্ট  
print("\n" + "="*60)  
print("✅ স্ক্র্যাপিং সম্পূর্ণ!")  
print("="*60)  
print(f"📅 শেষ সময়: {time.strftime('%Y-%m-%d %H:%M:%S')}")  
print(f"📈 মোট নতুন লিংক: {total_new_links}")  
print(f"📁 মোট ক্যাটাগরি: {len(CATEGORIES)}")  
  
# ক্যাটাগরি অনুযায়ী ফলাফল  
print("\n📊 ক্যাটাগরি অনুযায়ী ফলাফল:")  
print("-"*40)  
  
for category_name in CATEGORIES.keys():  
    filename = f"shuvo/{category_name}.txt"  
    if os.path.exists(filename):  
        with open(filename, "r", encoding="utf-8") as f:  
            lines = f.readlines()  
            link_count = 0  
            for line in lines:  
                if line.strip() and '://' in line and not line.startswith('#'):  
                    link_count += 1  
        print(f"📄 {category_name}: {link_count} লিংক")  
    else:  
        print(f"📄 {category_name}: 0 লিংক (ফাইল নেই)")  
  
print("-"*40)  
print(f"🎉 প্রোগ্রাম শেষ! 5 সেকেন্ড পর অটোমেটিক বন্ধ হবে...")  
print("="*60)  
  
# 5 সেকেন্ড অপেক্ষা করে অটোমেটিক বন্ধ  
time.sleep(5)  
sys.exit(0)

প্রোগ্রাম শুরু

if name == "main":
try:
main()
except KeyboardInterrupt:
print("\n\n❌ ব্যবহারকারী দ্বারা বন্ধ করা হয়েছে!")
sys.exit(1)
except Exception as e:
print(f"\n\n🔥 অপ্রত্যাশিত ত্রুটি: {e}")
sys.exit(1)

