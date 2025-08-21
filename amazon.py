from curl_cffi import requests
import lxml.html
import re
import json

def clean_text(text: str) -> str:
    if not text:
        return "N/A"
    return re.sub(r"[₹$,]", "", text).strip()

def extract_numeric(val: str, is_float=False):
    """Extract numbers from a string."""
    try:
        val = re.sub(r"[^\d.]", "", val)
        return float(val) if is_float else int(float(val))
    except:
        return None

def parse_amazon_page(asin: str) -> dict:
    url = f"https://www.amazon.in/dp/{asin}?th=1&psc=1"
    response = requests.get(url, impersonate="chrome110")
    try:
        if response.status_code == 200:
            tree = lxml.html.fromstring(response.text)

            # Product name via XPath
            product_title = tree.xpath('//h1/span[@id="productTitle"]/text()')
            product_title = product_title[0].strip() if product_title else None

            # Product name via turbo-checkout script
            turbo_block = re.search(
                r'<script[^>]+key[=\\"]+turbo-checkout-page-state[\\"]+[^>]*>\s*(\{.*?\})\s*</script>',
                response.text
            )
            turbo_data = json.loads(turbo_block.group(1)) if turbo_block else {}
            turbo_product_name = turbo_data.get("strings", {}).get("TURBO_CHECKOUT_HEADER", "").replace("Buy now:", "").strip()
            product_name = turbo_product_name if turbo_product_name else (product_title or "N/A")

            # Price via JSON
            json_price = None
            try:
                json_price_block = tree.xpath('//div[contains(@class,"twister-plus-buying-options-price-data")]/text()')[0]
                json_price_data = json.loads(json_price_block)
                price_info = json_price_data['desktop_buybox_group_1'][0]
                json_price = price_info.get('displayPrice')
            except Exception as e:
                print('Price JSON error:', e)

            # Price from price range
            price_range = tree.xpath('//span[@class="a-price a-text-price a-size-medium apexPriceToPay"]//span[@class="a-offscreen"]/text()')
            if len(price_range) == 2:
                formatted_price = f"{price_range[0]} - {price_range[1]}"
                price_numeric = [extract_numeric(p) for p in price_range]
            elif len(price_range) == 1:
                formatted_price = price_range[0]
                price_numeric = [extract_numeric(price_range[0])]
            else:
                formatted_price = None
                price_numeric = []

            fallback_price = tree.xpath('//span[@aria-hidden="true"]//span[@class="a-price-whole"]/text()')
            raw_price = json_price or formatted_price or (fallback_price[0] if fallback_price else "N/A")
            clean_price = extract_numeric(raw_price)

            # MRP
            mrp_xpath1 = tree.xpath('//span[@class="a-price a-text-price"]/span[@aria-hidden="true"]/text()')
            mrp_xpath2 = tree.xpath('//span[@class="aok-relative"]//span[@class="a-size-small aok-offscreen"]/text()')
            mrp_raw = mrp_xpath1[0] if mrp_xpath1 else (mrp_xpath2[0] if mrp_xpath2 else "N/A")
            mrp_clean = extract_numeric(mrp_raw.replace("M.R.P.:", ""))

            # Discount
            discount = tree.xpath('//span[contains(@class,"savingsPercentage")]/text()')
            discount_percent = extract_numeric(discount[0]) if discount else None

            # Avg Rating
            avg_rating = tree.xpath('//a/span[@class="a-size-base a-color-base"]/text()')
            average_rating = extract_numeric(avg_rating[0], is_float=True) if avg_rating else None

            # Rating count
            reviews = tree.xpath('//a/span[@id="acrCustomerReviewText"]/text()')
            review_count = extract_numeric(reviews[0]) if reviews else None

            # Main Image
            imgs1 = tree.xpath('//img[@class="a-dynamic-image"]/@src')
            imgs2 = tree.xpath('//div[@id="imgTagWrapperId"]/img/@src')
            main_image = imgs1[1] if len(imgs1) > 1 else (imgs2[0] if imgs2 else (imgs1[0] if imgs1 else "N/A"))

            # Thumbnails
            thumbnails = tree.xpath('//span[@class="a-button-text"]/img/@src')
            other_images = ",".join(thumbnails[1:]) if len(thumbnails) > 1 else ""

            # Brand
            brand = tree.xpath('//p/span[@class="a-size-medium a-text-bold"]/text()')
            brand_name = brand[0].strip() if brand else "N/A"

            # Stock status
            availability = tree.xpath('//span[@class="a-size-medium a-color-success"][contains(text(),"In stock")]/text()')
            stock_status = availability[0].strip() if availability else "N/A"

            # Category hierarchy
            categories = tree.xpath('//a[@class="a-link-normal a-color-tertiary"]/text()')
            category_hierarchy = {f"l{i+1}": cat.strip() for i, cat in enumerate(categories)} if categories else {}

            return {
                "currency": '₹',
                "product_name": product_name,
                "brand": brand_name,
                "main_image": main_image,
                "other_images": other_images,
                "product_price": clean_price,
                "mrp": mrp_clean,
                "discount_percent": discount_percent,
                "avg_rating": average_rating,
                "rating_count": review_count,
                "availability": stock_status,
                "category_hierarchy": category_hierarchy
            }

    except Exception as e:
        print("Error in parse_amazon_page:", e)
        return {
            "error": str(e),
            "product_name": "N/A"
        }

if __name__ == '__main__':
    asin = input("Enter an valid asin of amazon : ")
    data=parse_amazon_page(asin=asin)
    print(data)