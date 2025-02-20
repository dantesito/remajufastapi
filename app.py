from fastapi import FastAPI

schema_get_captcha = {
    "name": "lista productos",
    "baseSelector": ".product-item",
    "fields": [

        {
            "name": "nombre",
            "selector": ".product-info .product-name",
            "type": "text"
        }

    ]
}
app = FastAPI()
async def main():
   return {"say":schema_get_captcha}

#if __name__ == "__main__":
#    asyncio.run(main())
@app.get("/")
async def main():
  return await main()
