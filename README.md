# Cookie Jar

**Category:** Web  
**Difficulty:** Beginner  
**Flag format:** `GDG{...}`

## Description

Welcome to the Cookie Jar, where every login comes with a little something extra. We gave you a demo account and a warm welcome, but we may have handed you more than you noticed. Log in, take a look around, and see what's hiding in your jar.

**Demo account:** `user1` / `qwerty123`

## About the challenge

Cookie Jar is a small Flask app with a login page and a dashboard. After logging in, the server stores a signed JWT (JSON Web Token) in a `session` cookie. The flag is stored inside that token's payload.

The lesson: a JWT payload is only base64url-encoded, not encrypted. The signature stops people from *editing* a token, but anyone can *read* it.

## Hints

1. Look at what the server gives you when you log in.
2. Cookies that start with `eyJ` are worth a closer look.
3. The `X-Hint-3` response header says: "Have a close look at the Challenge name."

## Solution (organizers only)

1. Open the site and log in with `user1` / `qwerty123`.
2. Open dev tools (F12) → Application/Storage → Cookies, and copy the value of the `session` cookie.
3. Decode the token. Any of these works:
   - Paste it into [jwt.io](https://jwt.io). The "Invalid Signature" warning is expected and can be ignored.
   - CyberChef: use the "JWT Decode" operation.
   - Terminal: `echo '<middle part>' | base64 -d`
   - Python:
     ```python
     import base64, json
     token = "<cookie value>"
     part = token.split(".")[1]
     part += "=" * (-len(part) % 4)
     print(json.loads(base64.urlsafe_b64decode(part)))
     ```
4. The decoded payload contains the flag in the `flag` field:
   ```json
   {"user": "user1", "iat": 1762800000, "flag": "GDG{jwt_secrets_are_sweet_cookies}"}
   ```

No secret cracking or token forging is needed.

## Running locally

```bash
pip install flask pyjwt
python app.py
```

The app runs at `http://localhost:5000`.

To use `vercel dev` instead, which matches the production setup, run `vercel dev`.

## Configuration

| Variable     | Purpose                                     | Default                                |
|--------------|---------------------------------------------|----------------------------------------|
| `FLAG`       | The flag placed in the JWT payload          | `GDG{jwt_secrets_are_sweet_cookies}`   |
| `JWT_SECRET` | Key used to sign the JWT (HS256)            | A fixed fallback string                |

`JWT_SECRET` must be the same on every server instance, so set it as an environment variable when hosting on a serverless platform.

## Deploying to Vercel

1. Install the CLI: `npm i -g vercel`, then `vercel login`.
2. Add the environment variables:
   ```bash
   vercel env add JWT_SECRET
   vercel env add FLAG
   ```
3. Deploy: `vercel`, then `vercel --prod` to go live.

If you change an environment variable after deploying, redeploy so it takes effect.

## Files

- `app.py`: the Flask application (Vercel detects the top-level `app` variable)
- `requirements.txt`: Python dependencies (`flask`, `pyjwt`)
- `README.md`: this file

## Notes for organizers

- Change the flag before the event if you want a unique one.
- Remove this README (or at least the Solution section) from anything you share with players.
