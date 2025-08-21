# 🚀 Flipkart Product Scraper API + UI

A **FastAPI-based Flipkart Product Scraper** with a modern **Tailwind + Flowbite** UI.  
Easily fetch detailed product information such as **name, brand, price, MRP, ratings, reviews, delivery info, seller details, and images** from Flipkart product pages.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Render](https://img.shields.io/badge/Deploy%20on-Render-3b82f6?logo=render)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)

---

## ✨ Features

- 📦 **REST API** → `/scrape_flipkart` endpoint (JSON response)
- 🌐 **Modern Web UI** → TailwindCSS + Flowbite powered interface
- 📊 **Detailed Output**:
  - Product name & brand
  - Pricing (current price, MRP)
  - Ratings & total reviews
  - Seller info & return policy
  - Delivery info
  - Product images (main + gallery)
- 📑 **Interactive Swagger Docs** → `/docs`

---

## 🛠️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) (API Framework)
- [Jinja2](https://jinja.palletsprojects.com/) (Templates)
- [TailwindCSS](https://tailwindcss.com/) + [Flowbite](https://flowbite.com/) (UI)
- [curl_cffi](https://github.com/yifeikong/curl_cffi) (HTTP requests with browser impersonation)
- [lxml](https://lxml.de/) (HTML parsing)

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/flipkart-scraper.git
cd flipkart-scraper
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Locally
uvicorn main:app --reload --port 5000


Now visit 👉 http://127.0.0.1:5000
 for the UI
Swagger Docs 👉 http://127.0.0.1:5000/docs

☁️ Deploying on Render

Push your code to GitHub

Go to Render Dashboard

Create New Web Service

Connect your GitHub repo

Use the following settings:

Environment: Python 3

Build Command:

pip install -r requirements.txt


Start Command:

uvicorn main:app --host 0.0.0.0 --port 10000


Deploy 🚀

📂 Project Structure
.
├── main.py            # FastAPI app
├── helper.py          # Scraping logic
├── utils.py           # Utility functions (extract_json_data, get)
├── config.py          # Headers & constants
├── templates/
│   └── index.html     # Web UI (Tailwind + Flowbite)
├── requirements.txt   # Dependencies
└── README.md

📝 Example API Request
Request
POST /scrape_flipkart
Content-Type: application/json

{
  "url": "https://www.flipkart.com/product-sample-url?pid=XYZ123"
}

Response
{
  "product_name": "Sample Mobile Phone",
  "brand": "BrandX",
  "rating_count": "1,245",
  "average_rating": "4.3",
  "price": "14,999",
  "mrp": "19,999",
  "main_image_url": "https://.../main.jpg",
  "all_images": ["https://.../1.jpg", "https://.../2.jpg"],
  "delivery_by": "Tomorrow, 9 AM",
  "seller_name": "RetailNet",
  "return_policy": "7 Days Replacement Policy"
}

❤️ Contributing

PRs are welcome! Fork the repo, create a branch, make your changes, and submit a PR.