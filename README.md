# 🛒 E-Commerce Scraper & Price Comparison API (with Smart Title Matching)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Selenium](https://img.shields.io/badge/Automation-Selenium-orange.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An automated web scraping and price-comparison REST API built to aggregate, filter, and track product data across major Pakistani e-commerce platforms in real-time.

---

## 🌟 Key Highlights

* **Multi-Store Support:** Aggregates products from **Daraz.pk**, **Elo.shopping**, **iShopping.pk**, **Paklap.pk**, and **PriceOye.pk**.
* **Smart Title Matching Algorithm:** Unlike generic scrapers that return irrelevant search hits, this engine enforces multi-word query inclusion (`all(word in title)`), eliminating noise and returning accurate product matches.
* **Dual-Mode Engine:**
  1. **Listing Search:** Scrapes multi-page product listings with prices, ratings, images, and links.
  2. **Live Product Inspection:** Scrapes a specific product URL to extract up-to-the-minute price and real-time stock availability (`In Stock` / `Out of Stock`).
* **Hybrid Scraping:** Uses fast multi-threaded HTTP requests (`ThreadPoolExecutor` + `requests` + `BeautifulSoup`) where possible, and headless browser automation (`Selenium`) for JavaScript-heavy, dynamically rendered stores.
* **CORS & Network Ready:** Configured with Flask-CORS and binds to `0.0.0.0` for integration with mobile apps, web frontends, or browser extensions.

---

## 📁 Project Architecture

```
fypWithTitleMatching/
│── all_apis.py                  # Main Flask REST API server exposing all endpoints
│── darazheadlesschangeforapi.py # Headless Selenium scraper for Daraz search results
│── priceoyeheadless.py          # Headless Selenium scraper with infinite scroll for PriceOye
│── newishopping.py              # Multi-threaded concurrent scraper for iShopping
│── newpaklap.py                 # Automated paginated scraper for Paklap
│── newelo.py                    # Concurrent scraper & JSON-LD parser for Elo
│── requirements.txt             # Python dependencies
│── .gitignore                   # Excludes binaries, cache, and virtualenvs
└── README.md                    # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone & Set Up Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the API Server
```bash
python all_apis.py
```
The server will start on: `http://localhost:5000` (or `http://0.0.0.0:5000`).

---

## 🚗 ChromeDriver Guide: How It Works & How to Fix Outdated Drivers

### Why Does ChromeDriver Break?
When using **Selenium**, it controls Google Chrome through a companion binary called **`chromedriver.exe`**. 
Google Chrome updates automatically in the background. If your browser updates (e.g. from v132 to v134) while your local `chromedriver.exe` remains on an older version, Selenium throws this error:
> `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XYZ`

### How to Fix / Update It:

#### ✅ Option 1: Automatic Management via `webdriver-manager` (Recommended)
You can avoid manually downloading drivers forever by using `webdriver-manager`. In your Python code:
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Automatically downloads and matches the exact driver version for your installed Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
```

#### ✅ Option 2: Built-in Selenium Manager (Selenium 4.6+)
If you are using `selenium >= 4.6.0`, Selenium can automatically resolve and download the matching driver without specifying `executable_path`:
```python
from selenium import webdriver

# Simply omit the executable_path argument
driver = webdriver.Chrome(options=options)
```

#### ✅ Option 3: Manual Download
If you prefer a manual binary:
1. Check your Google Chrome version: Open Chrome -> Three Dots (Menu) -> **Help** -> **About Google Chrome** (e.g., `134.0.x`).
2. Download the matching ChromeDriver from the official Google testing dashboard:
   👉 [Chrome for Testing availability](https://googlechromelabs.github.io/chrome-for-testing/)
3. Extract `chromedriver.exe` and place it in this project folder (or add it to your system `PATH`).

---

## 📡 API Endpoints Reference

### 🔍 1. Product Search Endpoints (Listings)

| Endpoint | Method | Parameter | Description |
| :--- | :---: | :---: | :--- |
| `/daraz` | `GET` | `query=<item>` | Scrapes Daraz.pk with title matching |
| `/elo` | `GET` | `query=<item>` | Scrapes Elo.shopping (multi-page) |
| `/ishopping` | `GET` | `query=<item>` | Scrapes iShopping.pk with title matching |
| `/paklap` | `GET` | `query=<item>` | Scrapes Paklap.pk with title matching |
| `/priceoye` | `GET` | `query=<item>` | Scrapes PriceOye.pk with infinite scroll |

#### Example Request:
```bash
curl "http://localhost:5000/daraz?query=cat+food+fluffy"
```

#### Example Response:
```json
[
  {
    "Product Title": "Fluffy Cat Food 1.2kg Dry Food",
    "Product Price": "1250",
    "Product Old Price": "1400",
    "Product Rating": 4.5,
    "Product Rating Count": "(25)",
    "Availability": "In Stock",
    "Image URL": "https://img.drz.lazcdn.com/...",
    "Product URL": "https://www.daraz.pk/products/..."
  }
]
```

---

### 📦 2. Single Product Live Status Checkers

| Endpoint | Method | Parameter | Description |
| :--- | :---: | :---: | :--- |
| `/daraz/product` | `GET` | `query=<url>` | Live price & stock check for Daraz |
| `/elo/product` | `GET` | `query=<url>` | Live price & stock check for Elo |
| `/ishopping/product` | `GET` | `query=<url>` | Live price & stock check for iShopping |
| `/paklap/product` | `GET` | `query=<url>` | Live price & stock check for Paklap |
| `/priceoye/product` | `GET` | `query=<url>` | Live price & stock check for PriceOye |

#### Example Request:
```bash
curl "http://localhost:5000/priceoye/product?query=https://priceoye.pk/mobiles/samsung/samsung-galaxy-s24-ultra"
```

#### Example Response:
```json
{
  "Product Price": "399999",
  "Product Old Price": "434999",
  "Availability": "In Stock"
}
```

---

## 🎯 Smart Title Matching Explained

When searching for specific models (e.g. `Samsung S22` or `HP 840`), e-commerce search engines frequently return unrelated accessories (covers, chargers, screen protectors).

Our custom title-matching filter breaks down user query keywords:
```python
query_words = query.lower().split()
if all(word in product_title.lower() for word in query_words):
    # Only genuine matches are returned
```
This guarantees that all tokens from the user's search query are strictly verified before a product is appended to the results payload.

---

## 🛡️ License & Disclaimer
This project is developed for educational and research purposes (Final Year Project). When deploying scrapers, always adhere to the target websites' `robots.txt` and terms of service.
