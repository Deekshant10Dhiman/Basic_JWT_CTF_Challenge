"""app.py  --  pip install flask pyjwt

"Cookie Jar": a beginner JWT CTF modeled on the picoCTF-style challenges.
The flag sits in the JWT payload. Log in, grab the session cookie, decode it.

Run locally:  python app.py   (or: vercel dev)
Deploy:       vercel --prod
"""

import os
import datetime
import jwt
from flask import Flask, request, make_response, redirect, render_template_string

# Vercel looks for this top-level variable named `app`.
app = Flask(__name__)

FLAG = os.environ.get("FLAG", "GDG{jwt_secrets_are_sweet_cookies}")

# The secret MUST be the same on every serverless instance, so it comes from an
# environment variable (set JWT_SECRET in Vercel). A random per-process secret
# would make cookies fail whenever a request lands on a different instance.
# The fallback is a fixed string so things still work if the variable is missing;
# the flag is readable from the payload anyway, so the secret protects nothing here.
SECRET = os.environ.get(
    "JWT_SECRET", "cookie-jar-ctf-fixed-secret-0123456789abcdef0123456789abcdef"
)

# Starter credentials are given to the player.
USERS = {"user1": "qwerty123"}

PAGE = """
<!doctype html>
<title>Cookie Jar</title>
<body style="font-family: sans-serif; background-color: #1e1e1e; color: #eee;">
  <h1>Cookie Jar</h1>
  {{ body|safe }}
</body>
"""


def render(body, status=200):
    return make_response(render_template_string(PAGE, body=body), status)


def make_token(username):
    payload = {
        "user": username,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "flag": FLAG,
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def read_token():
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


@app.route("/")
def index():
    return render(
        """
        <p>Log in to view your account. New here? Use the demo account:</p>
        <p><code>user1</code> / <code>qwerty123</code></p>
        <form method="post" action="/login">
          <p><input name="username" placeholder="username"></p>
          <p><input name="password" type="password" placeholder="password"></p>
          <p><button>Log in</button></p>
        </form>
        """
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if USERS.get(username) != password:
        return render("<p>Wrong credentials.</p><p><a href='/'>Back</a></p>", 401)

    resp = make_response(redirect("/dashboard"))
    resp.set_cookie("session", make_token(username))
    return resp


@app.route("/dashboard")
def dashboard():
    claims = read_token()
    if not claims:
        return redirect("/")

    body = (
        f"<p>Welcome back, <b>{claims['user']}</b>.</p>"
        "<p>We handed you something at login. Have you looked at it?</p>"
    )
    resp = render(body)
    # Hint 3 visible in the inspector tab itself.
    resp.headers["X-Hint-3"] = "Have a close look at the Challenge name."
    return resp


if __name__ == "__main__":
    # Only used for local runs; Vercel serves `app` directly.
    app.run(host="0.0.0.0", port=5000)
