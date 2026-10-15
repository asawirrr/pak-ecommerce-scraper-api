# 📦 FYP E-Commerce Scraper (v1 - Intermediate Archive)

> **Notice:** This branch contains the intermediate version (v1) of the scraping engine. For the latest production version featuring the **Smart Title Matching Algorithm**, please refer to the main branch.

---

## 📌 Overview
This folder contains the consolidated multi-store scraper and REST API before the implementation of word-by-word title filtering.

### Supported Stores:
* Daraz.pk
* Elo.shopping
* iShopping.pk
* Paklap.pk
* PriceOye.pk (Selenium headless)

---

## 🚀 Setup & Execution

`ash
# Setup virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python all_apis.py
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
