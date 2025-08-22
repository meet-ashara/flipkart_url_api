import logging
from lxml import html
from curl_cffi import requests
from utils import extract_json_data, get
from config import headers
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse

# Setup logger
logger = logging.getLogger("flipkart_scraper")
logger.setLevel(logging.INFO)

def get_from_paths(data, paths, field_name, fallback=None):
    """
    Try multiple JSON paths and return the first valid value.
    Logs a warning if all fail.
    """
    for path in paths:
        val = get(data, path)
        if val != "N/A":
            return val
    logger.warning(f"[SCRAPER] {field_name} not found, using fallback: {fallback}")
    return fallback or "N/A"

def scrape_flipkart_product(url: str):
    if "flipkart.com" not in url:
        raise HTTPException(status_code=403 ,detail="Invalid Flipkart URL")
    if "pid=" not in url:
        raise HTTPException(status_code=403 ,detail="URL does not contain product ID")
    try:
        res = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        res.raise_for_status()
    except Exception as e:
        logger.error(f"[SCRAPER] Failed request for {url}: {e}")
        return {"error": str(e), "url": url}

    html_text = res.text
    tree = html.fromstring(html_text)
    data = extract_json_data(html_text)

    # Product name
    product_name = get_from_paths(data, [
        ["pageDataV4","page","data","10002",2,"widget","data","titleComponent","value","title"],
        ["pageDataV4","page","pageData","pageContext","seo","title"],
    ], "product_name", fallback=tree.xpath('//span[@class="VU-ZEz"]/text()[1]'))
    if isinstance(product_name, list):
        product_name = product_name[0].strip() if product_name else "N/A"

    # Brand
    brand = get_from_paths(data, [
        ["pageDataV4","page","pageData","seoData","schema",0,"brand","name"]
    ], "brand", fallback=tree.xpath('//span[@class="mEh187"]/text()'))
    if isinstance(brand, list):
        brand = brand[0].strip() if brand else "N/A"

    # Ratings
    number_of_ratings = get_from_paths(data, [
        ["pageDataV4","page","data","10002",1,"widget","data","ratingsAndReviews","value","rating","count"]
    ], "rating_count")

    avg_rating = get_from_paths(data, [
        ["pageDataV4","page","data","10002",1,"widget","data","ratingsAndReviews","value","rating","average"]
    ], "average_rating")

    # Images
    main_url = tree.xpath('//img[@class="_53J4C- utBuJY"]/@src')
    if not main_url:
        main_url = tree.xpath('//img[@class="DByuf4 IZexXJ jLEJ7H"]/@src')
    image_urls = tree.xpath('//img[@class="_0DkuPH"]/@src')
    main_url = main_url[0] if main_url else (image_urls[0] if image_urls else "N/A")

    # Pricing (multiple fallback JSON paths)
    product_price = get_from_paths(data, [
        ["pageDataV4","page","pageData","pageContext","fdpEventTracking","events","psi","ppd","finalPrice"],
        ["pageDataV4","page","pageData","pageContext","pricing","prices",0,"decimalValue"],
    ], "product_price", fallback=tree.xpath('//div[@class="Nx9bqj CxhGGd"]/text()'))
    if isinstance(product_price, list):
        product_price = product_price[0].strip() if product_price else "N/A"

    product_mrp = get_from_paths(data, [
        ["pageDataV4","page","pageData","pageContext","fdpEventTracking","events","psi","ppd","mrp"],
        ["pageDataV4","page","pageData","pageContext","pricing","mrp"],
        ["pageDataV4","page","data","10002",1,"widget","data","pricing","value","prices",0,"value"],
    ], "mrp")

    # Delivery by (multiple fallbacks)
    delivery_by = get_from_paths(data, [
        ["pageDataV4","page","data","10002",4,"widget","data","deliveryData","messages",0,"value","dateText"],
        ["pageDataV4","page","data","10002",4,"widget","data","deliveryData","messages",1,"value","dateText"],
        ["pageDataV4","page","pageData","pageContext","trackingDataV2","slaText"],
    ], "delivery_by")

    # Seller info
    seller_name = get_from_paths(data, [
        ["pageDataV4","page","pageData","pageContext","trackingDataV2","sellerName"]
    ], "seller_name")

    # Category
    category = get_from_paths(data, [
        ["pageDataV4","page","data","10005",4,"widget","data","parentProduct","value","analyticsData","vertical"]
    ], "category")

    # Return policy (multiple fallbacks)
    return_policy = get_from_paths(data, [
        ["pageDataV4","page","data","10005",0,"widget","data","SellerMetaValue","value","returnCallouts",0,"displayText"],
        ["pageDataV4","page","data","10005",1,"widget","data","deliveryData","deliveryCallouts",0,"value","text"],
    ], "return_policy")

    return {"product_name": product_name,
        "brand": brand,
        "rating_count": number_of_ratings,
        "average_rating": avg_rating,
        "price": product_price,
        "mrp": product_mrp,
        "main_image_url": main_url,
        "all_images": image_urls,
        "category":category,    
        "delivery_by": delivery_by,
        "seller_name": seller_name,
        "return_policy": return_policy
    }
