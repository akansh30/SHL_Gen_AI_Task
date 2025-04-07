from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Type code to full name mapping
type_map = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

BASE_URL = "https://www.shl.com"
CATALOG_URL = BASE_URL + "/solutions/products/product-catalog/"

# Setup headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

print("Loading catalog...")
driver.get(CATALOG_URL)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

# Extract product links and test type codes
products = []

while True:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for row in rows:
        try:
            link_elem = row.find_element(By.CSS_SELECTOR, "td a")
            name = link_elem.text.strip()
            url = link_elem.get_attribute("href")

            badges = row.find_elements(By.CSS_SELECTOR, "td:nth-child(4) span")
            test_type_codes = [badge.text.strip() for badge in badges if badge.text.strip()]
            full_types = ", ".join([type_map.get(t, t) for t in test_type_codes])

            # Adaptive and Remote Testing checks
            adaptive = False
            remote = False
            try:
                adaptive_icon = row.find_element(By.XPATH, './td[5]//span[contains(@class,"catalogue_circle -yes")]')
                adaptive = True
            except:
                pass
            try:
                remote_icon = row.find_element(By.XPATH, './td[6]//span[contains(@class,"catalogue_circle -yes")]')
                remote = True
            except:
                pass

            products.append({
                "name": name,
                "url": url,
                "test_types": full_types,
                "adaptive": adaptive,
                "remote": remote
            })
        except Exception as e:
            print(f"Skipping row due to error: {e}")

    # Click the next page button if it exists and is enabled
    try:
        next_btn = driver.find_element(By.LINK_TEXT, "Next")
        if "disabled" in next_btn.get_attribute("class") or not next_btn.is_displayed():
            break
        next_btn.click()
    except:
        break

print(f"Found {len(products)} products...")

# Visit each product page to fetch details
data = []

def get_detail_fields():
    fields = {
        "Description": "",
        "Job levels": "",
        "Languages": "",
        "Assessment length": ""
    }
    try:
        detail_blocks = driver.find_elements(By.CSS_SELECTOR, ".product-catalogue-training-calendar__row.typ")
        for block in detail_blocks:
            try:
                heading = block.find_element(By.TAG_NAME, "h4").text.strip()
                value_elem = block.find_element(By.TAG_NAME, "p")
                value = value_elem.text.strip()
                if "Completion Time" in value:
                    value = value.replace("Approximate Completion Time in minutes =", "").strip()
                fields[heading] = value
            except:
                continue
    except:
        pass
    return fields

for idx, product in enumerate(products):
    print(f"[{idx+1}/{len(products)}] Visiting: {product['url']}")
    driver.get(product["url"])

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
    except:
        print("⚠️ Timeout waiting for page to load.")
        continue

    name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    details = get_detail_fields()

    data.append({
        "Assessment Name": name,
        "URL": product["url"],
        "Test Types": product.get("test_types", ""),
        "Adaptive": product.get("adaptive", False),
        "Remote": product.get("remote", False),
        "Description": details.get("Description", ""),
        "Job Levels": details.get("Job levels", ""),
        "Languages": details.get("Languages", ""),
        "Assessment Length": details.get("Assessment length", "")
    })

    # Save intermediate progress
    if (idx + 1) % 10 == 0:
        pd.DataFrame(data).to_csv("shl_assessments_progress.csv", index=False)
        print("💾 Progress saved.")

# Final save
df = pd.DataFrame(data)
df.to_csv("shl_assessments_full.csv", index=False)
print("✅ Data saved to shl_assessments_full.csv")

driver.quit()
