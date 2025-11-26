#1
from flask import Flask
from threading import Thread

#2
app = Flask('')

#3
@app.route('/')
def home():
    return "Bot is alive!"

#4
def run():
    app.run(host="0.0.0.0", port=8080)

#5
def keep_alive():
    t = Thread(target=run)
    t.start()