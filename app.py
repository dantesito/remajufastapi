from flask import Flask, request
app = Flask(__name__)
@app.route("/")
async def hello():
    return {"ko":"der"}