# Cookie Jar: Full Walkthrough

**Category:** Web | **Difficulty:** Beginner | **Flag format:** `GDG{...}`

> Spoiler warning: this document contains the complete solution. Do not share it with players.

---

## 1. Challenge summary

| Item            | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| Given           | A website with a login form and a demo account                |
| Credentials     | `user1` / `qwerty123`                                         |
| Goal            | Find the flag, formatted as `GDG{...}`                        |
| Core concept    | A JWT payload is base64url-encoded, **not encrypted**         |
| Skills involved | Browser dev tools, cookies, base64, reading JWTs              |

Description shown to players:

> Welcome to the Cookie Jar, where every login comes with a little something extra. We gave you a demo account and a warm welcome, but we may have handed you more than you noticed. Log in, take a look around, and see what's hiding in your jar.

---

## 2. Background: what is a JWT?

A JSON Web Token is a string made of three parts separated by dots:

```
header.payload.signature
```

| Part      | Contents                                         | Encoding         |
|-----------|--------------------------------------------------|------------------|
| Header    | `{"alg":"HS256","typ":"JWT"}`                    | base64url        |
| Payload   | Claims such as the user, issue time, and here the flag | base64url  |
| Signature | HMAC-SHA256 of `header.payload` using a secret   | base64url        |

Two facts matter for this challenge:

1. **The signature protects integrity, not secrecy.** If you edit the payload, the signature no longer matches and the server rejects the token.
2. **The payload is readable by anyone.** Base64url is an encoding, not encryption. No key is needed to decode it.

Every JWT header begins with `eyJ`, because that is what `{"` looks like in base64. That makes JWTs easy to spot in cookies.

---

## 3. Step-by-step solution

### Step 1: Explore the site

Open the challenge URL. You see a login page that shows the demo account:

```
user1 / qwerty123
```

### Step 2: Log in

Enter the credentials and submit. You are redirected to `/dashboard`, which says:

> Welcome back, **user1**.  
> We handed you something at login. Have you looked at it?

That sentence is the nudge. The server gave you something at login, so look at what the browser received.

### Step 3: Find what the server gave you

There are two places to look.

**Cookies.** Open dev tools with `F12`, then go to:
- Chrome / Edge: Application → Cookies
- Firefox: Storage → Cookies

You will see a cookie named `session` with a long value that starts with `eyJ`.

**Response headers.** In the Network tab, click the `/dashboard` request and open the response headers. There you will find:

```
X-Hint-3: Have a close look at the Challenge name.
```

"Cookie Jar" points to the cookie.

### Step 4: Recognize the token as a JWT

The value looks like this (shortened):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlcjEiLCJpYXQiOjE3NjI4MDAwMDAsImZsYWciOiJHREd7...}.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

The clues are:
- It starts with `eyJ`.
- It has exactly two dots, giving three parts.

That is the shape of a JWT.

### Step 5: Decode it

Copy the cookie value and decode it with any one of these methods.

**Option A: jwt.io (easiest)**
1. Go to https://jwt.io.
2. Paste the token into the encoded box.
3. The decoded payload appears on the right.

The signature section may show "Invalid Signature", or a placeholder secret such as `a-string-secret-at-least-256-bits-long`. This is expected. jwt.io does not know the server's secret. Decoding does not need it, so ignore the warning.

**Option B: CyberChef**
1. Open CyberChef and add the **JWT Decode** operation.
2. Paste the token as input.

**Option C: Browser console**
```js
JSON.parse(atob("PASTE_MIDDLE_PART".replace(/-/g, "+").replace(/_/g, "/")))
```
Take only the middle part (between the two dots). The `replace` calls convert base64url to standard base64.

**Option D: Terminal**
```bash
echo 'PASTE_MIDDLE_PART' | base64 -d
```
This may print a padding warning, but the output is usually still readable.

**Option E: Python**
```python
import base64, json

token = "PASTE_FULL_COOKIE_VALUE"
payload_b64 = token.split(".")[1]
payload_b64 += "=" * (-len(payload_b64) % 4)   # restore the stripped padding
print(json.loads(base64.urlsafe_b64decode(payload_b64)))
```

### Step 6: Read the flag

The decoded payload looks like this:

```json
{
  "user": "user1",
  "iat": 1762800000,
  "flag": "GDG{jwt_secrets_are_sweet_cookies}"
}
```

**Flag:** `GDG{jwt_secrets_are_sweet_cookies}`

(If the organizers changed the `FLAG` environment variable, the value will differ.)

---

## 4. Why it works: the vulnerability

The server builds the token like this:

```python
payload = {
    "user": username,
    "iat": datetime.datetime.now(datetime.timezone.utc),
    "flag": FLAG,
}
return jwt.encode(payload, SECRET, algorithm="HS256")
```

The developer put sensitive data (`flag`) inside the payload and assumed signing would protect it. Signing only stops tampering. The data is still sent to the client in readable form on every request.

On the server side, `read_token()` verifies the signature correctly and only accepts `HS256`, so:
- Forging a token without the secret fails.
- The `alg: none` trick fails.
- Cracking the secret is unnecessary, because the flag is already visible.

---

## 5. Common mistakes and dead ends

| Mistake | Why it doesn't help |
|---------|---------------------|
| Trying to brute-force the JWT secret | The secret is random and long, and the flag does not need it |
| Trying the `alg: none` attack | The server only accepts `HS256` |
| Looking for `/admin` or other routes | The app has only `/`, `/login`, and `/dashboard` |
| Trying SQL injection on the login form | There is no database, only a fixed user dictionary |
| Panicking about "Invalid Signature" on jwt.io | Decoding works without the key, so this is expected |
| Forgetting base64url padding in scripts | Add `=` characters until the length is a multiple of 4 |

---

## 6. Real-world lessons

1. **Never put secrets in a JWT payload.** Treat it as public information.
2. **Signed does not mean encrypted.** If the contents must be hidden, use encrypted tokens (JWE) or keep the data on the server and store only a session ID in the cookie.
3. **Store only what the client needs**, such as a user ID and expiry.
4. **Mark session cookies `HttpOnly`, `Secure`, and `SameSite`** in production. This challenge deliberately leaves the defaults so the cookie is easy to inspect.

---

## 7. Hint ladder for organizers

If players get stuck, release hints in this order:

1. "Look at what the server gives you when you log in."
2. "Search the Headers" [Headers contain the hint as 'X-Hint-3']
3. "Cookies that start with `eyJ` are worth a closer look."

---

## 8. Quick reference

```
1. Log in            user1 / qwerty123
2. Open dev tools    F12 -> Cookies -> session
3. Copy the token    starts with eyJ, has two dots
4. Decode it         jwt.io / CyberChef / base64 -d
5. Read "flag"       GDG{jwt_secrets_are_sweet_cookies}
```
