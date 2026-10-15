# 🧪 Developer Sandbox & Experiments (Archive)

> **Notice:** This branch contains experimental scripts, scratchpads, and individual test APIs created during early development (Stage 1).

---

## 🔬 Directory Contents
* **Individual API Scripts:** pidaraz.py, pielo.py, piishopping.py, pipaklap.py, pipriceoye.py
* **Single Product Checkers:** pi_product_daraz.py, pi_product_elo.py, pi_product_ishopping.py, pi_product_paklap.py, pi_product_priceoye.py
* **Experimental Code:** daraz_without_headless.py, 
ewpriceoye.py (early requests-based attempt), ytselenium.py, elobys.py, myselenium.py, image.py
* **Draft Master Server:** ll_apis.py (Early prototype)

---

## ⚙️ Running Individual Tests
Each script can be run standalone for isolated debugging:
`ash
python apidaraz.py
python api_product_daraz.py
`

---

## 🚗 ChromeDriver Guide: How It Works & How to Fix Outdated Drivers

### Why Does ChromeDriver Break?
When using **Selenium**, it controls Google Chrome through a companion binary called **chromedriver.exe**. 
Google Chrome updates automatically in the background. If your browser updates (e.g., from v132 to v134) while your local chromedriver.exe remains on an older version, Selenium throws this error:
> SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XYZ

### How to Fix / Update It:

#### ✅ Option 1: Automatic Management via webdriver-manager (Recommended)
You can avoid manually downloading drivers forever by using webdriver-manager. In your Python code:
`python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Automatically downloads and matches the exact driver version for your installed Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
`

#### ✅ Option 2: Built-in Selenium Manager (Selenium 4.6+)
If you are using selenium >= 4.6.0, Selenium can automatically resolve and download the matching driver without specifying executable_path:
`python
from selenium import webdriver

# Simply omit the executable_path argument
driver = webdriver.Chrome(options=options)
`

#### ✅ Option 3: Manual Download
If you prefer a manual binary:
1. Check your Google Chrome version: Open Chrome -> Three Dots (Menu) -> **Help** -> **About Google Chrome** (e.g., 134.0.x).
2. Download the matching ChromeDriver from the official Google testing dashboard:
   👉 [Chrome for Testing availability](https://googlechromelabs.github.io/chrome-for-testing/)
3. Extract chromedriver.exe and place it in this project folder (or add it to your system PATH).
