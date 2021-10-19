import os
from flask import Flask
if os.path.exists("env.py"):
    import env

# create an instance of Flask called app
app = Flask(__name__)


# application running instructions by retieving hidden env variables
if __name__ == "__main__":
    # retrieve the hidden env values and set them in variables
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)# this only used in development to debug

