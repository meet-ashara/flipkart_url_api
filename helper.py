from lxml import html
from curl_cffi import requests
from utils import extract_json_data, get
from config import headers

def scrape_flipkart_product(url: str):
    res = requests.get(url, headers=headers, impersonate="chrome110")
    res.raise_for_status()

    html_text = res.text
    tree = html.fromstring(html_text)
    data = extract_json_data(html_text)

    # Product name
    product_name = get(data, ["pageDataV4","page","data","10002",2,"widget","data","titleComponent","value","title"])
    if product_name == 'N/A':
        product_name = get(data, ["pageDataV4","page","pageData","pageContext","seo","title"])
    if product_name == 'N/A':
        product_name = tree.xpath('//span[@class="VU-ZEz"]/text()[1]')
        product_name = product_name[0].strip() if product_name else 'N/A'

    # Brand
    brand = get(data, ["pageDataV4","page","pageData","seoData","schema",0,"brand","name"])
    if brand == 'N/A':
        brand = tree.xpath('//span[@class="mEh187"]/text()')
        brand = brand[0].strip() if brand else 'N/A'

    # Ratings
    number_of_ratings = get(data, ["pageDataV4","page","data","10002",1,"widget","data","ratingsAndReviews","value","rating","count"])
    avg_rating = get(data, ["pageDataV4","page","data","10002",1,"widget","data","ratingsAndReviews","value","rating","average"])

    # Images
    main_url = tree.xpath('//img[@class="_53J4C- utBuJY"]/@src')
    if not main_url:
        main_url = tree.xpath('//img[@class="DByuf4 IZexXJ jLEJ7H"]/@src')
    image_urls = tree.xpath('//img[@class="_0DkuPH"]/@src')
    main_url = main_url[0] if main_url else (image_urls[0] if image_urls else 'N/A')

    # Pricing
    product_price = get(data, ["pageDataV4","page","pageData","pageContext","fdpEventTracking","events","psi","ppd","finalPrice"])
    if product_price == 'N/A':
        product_price = tree.xpath('//div[@class="Nx9bqj CxhGGd"]/text()')
        product_price = product_price[0].strip() if product_price else 'N/A'

    product_mrp = get(data, ["pageDataV4","page","pageData","pageContext","fdpEventTracking","events","psi","ppd","mrp"])

    # Delivery
    # delivery_by = get(data, ["pageDataV4","page","data","10002",3,"widget","data","deliveryData","messages",0,"value","dateText"])
    # if  not delivery_by:
    delivery_by = get(data, ["pageDataV4","page","data","10002",4,"widget","data","deliveryData","messages",1,"value","dateText"])


    # Seller info
    seller_name = get(data, ["pageDataV4","page","pageData","pageContext","trackingDataV2","sellerName"])
    return_policy = get(data, ["pageDataV4","page","data","10005",0,"widget","data","SellerMetaValue","value","returnCallouts",0,"displayText"])

    return {
        "product_name": product_name,
        "brand": brand,
        "rating_count": number_of_ratings,
        "average_rating": avg_rating,
        "price": product_price,
        "mrp": product_mrp,
        "main_image_url": main_url,
        "all_images": image_urls,
        "delivery_by": delivery_by,
        "seller_name": seller_name,
        "return_policy": return_policy
    }
