from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from helper import scrape_flipkart_product

# Initialize FastAPI
app = FastAPI(
    title="Flipkart Product Scraper API",
    description="🚀 A simple API + UI to scrape product details from Flipkart",
    version="1.0.0"
)

# Templates setup
templates = Jinja2Templates(directory="templates")

# Request model for API
class FlipkartRequest(BaseModel):
    url: str

# --------------------------
# API Endpoints
# --------------------------

# JSON API
@app.post("/scrape_flipkart")
async def scrape_flipkart(request: FlipkartRequest):
    url = request.url.strip()

    if "flipkart.com" not in url:
        raise HTTPException(status_code=400, detail="Invalid Flipkart URL")
    if "pid=" not in url:
        raise HTTPException(status_code=400, detail="URL does not contain product ID")

    try:
        return scrape_flipkart_product(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape: {str(e)}")

# Health
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Flipkart API is running fine ✅"}

# UI homepage
@app.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": None, "error": None})

# UI form POST
@app.post("/scrape-ui", response_class=HTMLResponse)
async def scrape_from_ui(request: Request, url: str = Form(...)):
    try:
        result = scrape_flipkart_product(url)
        return templates.TemplateResponse("index.html", {"request": request, "data": result, "url": url, "error": None})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "data": None, "url": url, "error": str(e)})

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
