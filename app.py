from flask import Flask
import nest_asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from base64 import b64decode
import base64
from playwright.async_api import Page, BrowserContext
import json
import socket
from PIL import Image
from io import BytesIO

import os
import math
from collections import Counter
import re
from pydantic import BaseModel, Field
nest_asyncio.apply()
import time

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='remaju.json'
WORD = re.compile(r"\w+")

def base64_to_image(base64_string):
  # Remove the data URI prefix if present
  if "data:image" in base64_string:
      base64_string = base64_string.split(",")[1]
      print(base64_string)

  # Decode the Base64 string into bytes
  image_bytes = base64.b64decode(base64_string)
  return image_bytes

def create_image_from_bytes(image_bytes):
  # Create a BytesIO object to handle the image data
  image_stream = BytesIO(image_bytes)

  # Open the image using Pillow (PIL)
  image = Image.open(image_stream)
  return image

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    # for non-dense text 
    # response = client.text_detection(image=image)
    # for dense text
    response = client.text_detection(image=image)
    texts = response.text_annotations
    #print(texts)
    ocr_text = ""

    for text in texts:
        ocr_text = text.description

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    
    return ocr_text

def find_open_port():
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a random available port
    sock.bind(('127.0.0.1', 0))

    # Get the port that was actually bound
    _, port = sock.getsockname()

    # Close the socket
    sock.close()

    return port

schema_get_captcha = {
     "name": "Commit Extractor",
            "baseSelector": ".ui-inputgroup",
            "fields": [
                {
                    "name": "src",
                    "selector": ".captcha-img-fix",
                    "type": "attribute",
                    "attribute":"src"
                    
                },
            ],
}
extraction_strategy = JsonCssExtractionStrategy(schema_get_captcha)


app = Flask(__name__)

@app.route('/')
async def hello_world():
    
    # 1) Configure the browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )

    # 2) Configure the crawler run
    strategy = JsonCssExtractionStrategy(schema_get_captcha)
    #js_code = 'document.querySelector(".ui-inputgroup .captcha-img-fix").src'#diseñado para realizar acciones

    crawler_run_config = CrawlerRunConfig(
        #js_code="window.scrollTo(0, document.body.scrollHeight);",
        #wait_for="body",
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        #screenshot=True,
        

    )
    

    # 3) Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()
    # 4) Run the crawler on an example page
    url = "https://remaju.pj.gob.pe/remaju/pages/seguridad/login.xhtml"
    result = await crawler.arun(url, config=crawler_run_config)

    if result.success:
        #print("\nCrawled URL:", result.extracted_content)
        news_teasers = result.markdown
        print(news_teasers)
            #print(f"Successfully extracted {len(news_teasers)} news teasers")
            #imagen64 = news_teasers[0]
            #print(imagen64)
            #image_bytes = base64_to_image(imagen64['src'])
            # Create an image from bytes
            #img = create_image_from_bytes(image_bytes)
            # Display or save the image as needed
            #img.show()
            #img.save("output_image.jpg")
            #print(detect_text('output_image.jpg'))
            #______#
            #print(result.markdown)
            #if result.screenshot:
            #    with open("result.png", "wb") as f:
            #        f.write(b64decode(result.screenshot))

    else:
            print("Error:", result.error_message)

    await crawler.close()

    return {"jo":"der"}


if __name__ == "__main__":
    app.run()