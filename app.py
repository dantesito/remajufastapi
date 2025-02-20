from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main(request):
    return {"ko":"der"}


if __name__ == "__main__":
    app.run()