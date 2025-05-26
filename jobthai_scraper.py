import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep

# STEP 1: ดึงชื่อบริษัทจาก JobThai
def get_company_names_from_jobthai(pages=1):
    all_companies = []
    for page in range(1, pages + 1):
        url = f"{page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        company_tags = soup.select("div.company-info h3")
        if not company_tags:
            break
        for tag in company_tags:
            name = tag.text.strip()
            all_companies.append(name)
        sleep(1)
    return all_companies

# STEP 2: ค้นหาเว็บไซต์ด้วย SerpAPI
def search_company_website(company_name, api_key):
    params = {
        "q": company_name,
        "api_key": api_key,
        "engine": "google",
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params)
        data = res.json()
        for result in data.get("organic_results", []):
            link = result.get("link")
            if link and "http" in link:
                return link
    except:
        return None
    return None

# STEP 3: ดึง Email จากเว็บไซต์
def get_email_from_website(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return list(set(emails))
    except:
        return []

# STEP 4: รวมข้อมูล
def collect_company_data(pages, serpapi_key):
    companies = get_company_names_from_jobthai(pages)
    data = []
    for company in companies:
        print(f"🔍 ค้นหา: {company}")
        website = search_company_website(company, serpapi_key)
        emails = get_email_from_website(website) if website else []
        data.append({
            "Company": company,
            "Website": website,
            "Emails": ", ".join(emails)
        })
        sleep(1)
    return pd.DataFrame(data)

# MAIN RUN
if __name__ == "__main__":
    SERP_API_KEY = "YOUR_SERPAPI_KEY_HERE"  # <<== ใส่ key ของคุณตรงนี้
    df = collect_company_data(pages=2, serpapi_key=SERP_API_KEY)
    df.to_excel("jobthai_companies.xlsx", index=False)
    print("✅ บันทึกข้อมูลลงไฟล์ jobthai_companies.xlsx แล้ว")
