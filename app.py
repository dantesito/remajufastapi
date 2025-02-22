from flask import Flask
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from base64 import b64decode
from playwright.async_api import Page, BrowserContext
import json
import socket

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
    "name": "captcha",
    "baseSelector": ".product-item",
    "fields": [

        {
            "name": "nombre",
            "selector": ".product-info .product-name",
            "type": "text"
        }

    ]
}


app = Flask(__name__)

@app.route('/')
async def hello_world():
    

    print("🔗 Hooks Example: Demonstrating recommended usage")

    # 1) Configure the browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )

    # 2) Configure the crawler run
    strategy = JsonCssExtractionStrategy(schema_get_captcha)
    crawler_run_config = CrawlerRunConfig(
        #js_code="window.scrollTo(0, document.body.scrollHeight);",
        #wait_for="body",
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        screenshot=True,

    )

    # 3) Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)

    #
    # Define Hook Functions
    #

    async def on_browser_created(browser, **kwargs):
        # Called once the browser instance is created (but no pages or contexts yet)
        print("[HOOK] on_browser_created - Browser created successfully!")
        # Typically, do minimal setup here if needed
        return browser

    async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
        # Called right after a new page + context are created (ideal for auth or route config).
        print("[HOOK] on_page_context_created - Setting up page & context.")
        await page.goto("https://remaju.pj.gob.pe/remaju/pages/seguridad/login.xhtml")
        await page.click('.ui-corner-left')
        await page.fill('.ui-inputtext', "191543")
        await page.fill('.ui-password', "Messenger2")
        await page.fill('.captcha-input', "Messenger2")
        await page.click("button[type='submit']")
        await page.wait_for_selector("#page-title")

        # Example 1: Route filtering (e.g., block images)
        #async def route_filter(route):
        #    if route.request.resource_type == "image":
        #        print(f"[HOOK] Blocking image request: {route.request.url}")
        #        await route.abort()
        #    else:
        #        await route.continue_()

        #await context.route("**", route_filter)

        # Example 2: (Optional) Simulate a login scenario
        # (We do NOT create or close pages here, just do quick steps if needed)
        # e.g., await page.goto("https://example.com/login")
        # e.g., await page.fill("input[name='username']", "testuser")
        # e.g., await page.fill("input[name='password']", "password123")
        # e.g., await page.click("button[type='submit']")
        # e.g., await page.wait_for_selector("#welcome")
        # e.g., await context.add_cookies([...])
        # Then continue

        # Example 3: Adjust the viewport
        await page.set_viewport_size({"width": 1080, "height": 600})
        return page

    async def before_goto(
        page: Page, context: BrowserContext, url: str, **kwargs
    ):
        # Called before navigating to each URL.
        print(f"[HOOK] before_goto - About to navigate: {url}")
        # e.g., inject custom headers
        await page.set_extra_http_headers({
            "Custom-Header": "my-value"
        })
        return page

    async def after_goto(
        page: Page, context: BrowserContext,
        url: str, response, **kwargs
    ):
        # Called after navigation completes.
        print(f"[HOOK] after_goto - Successfully loaded: {url}")
        # e.g., wait for a certain element if we want to verify
        try:
            await page.wait_for_selector('.catalog', timeout=1000)
            print("[HOOK] Found .content element!")
        except:
            print("[HOOK] .content not found, continuing anyway.")
        return page

    async def on_user_agent_updated(
        page: Page, context: BrowserContext,
        user_agent: str, **kwargs
    ):
        # Called whenever the user agent updates.
        print(f"[HOOK] on_user_agent_updated - New user agent: {user_agent}")
        return page

    async def on_execution_started(page: Page, context: BrowserContext, **kwargs):
        # Called after custom JavaScript execution begins.
        print("[HOOK] on_execution_started - JS code is running!")
        return page

    async def before_retrieve_html(page: Page, context: BrowserContext, **kwargs):
        # Called before final HTML retrieval.
        print("[HOOK] before_retrieve_html - We can do final actions")
        # Example: Scroll again
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        return page

    async def before_return_html(
        page: Page, context: BrowserContext, html: str, **kwargs
    ):
        # Called just before returning the HTML in the result.
        print(f"[HOOK] before_return_html - HTML length: {len(html)}")
        return page

    #
    # Attach Hooks
    #

    crawler.crawler_strategy.set_hook("on_browser_created", on_browser_created)
    crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
    crawler.crawler_strategy.set_hook("before_goto", before_goto)
    crawler.crawler_strategy.set_hook("after_goto", after_goto)
    crawler.crawler_strategy.set_hook("on_user_agent_updated", on_user_agent_updated)
    crawler.crawler_strategy.set_hook("on_execution_started", on_execution_started)
    crawler.crawler_strategy.set_hook("before_retrieve_html", before_retrieve_html)
    crawler.crawler_strategy.set_hook("before_return_html", before_return_html)

    await crawler.start()

    # 4) Run the crawler on an example page
    url = "https://www.scrapingcourse.com/dashboard"
    result = await crawler.arun(url, config=crawler_run_config)

    if result.success:
        print("\nCrawled URL:", result.url)
        print(result.markdown)
        if result.screenshot:
            with open("result.png", "wb") as f:
                f.write(b64decode(result.screenshot))
    else:
        print("Error:", result.error_message)

    await crawler.close()
    data = json.loads(result.extracted_content)
    return data


if __name__ == "__main__":
    app.run()