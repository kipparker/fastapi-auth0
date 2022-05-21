# Simple FastAPI and Auth0 authentication

I was looking around for examples of how to do this and everything was a bit too complex or lengthy for the simple application I had in mind. This is a bare bones example you can build what you need with.

Let start with the Auth0 part. Log in to your account, go to Applications > APIs and click on Create API. Enter a name and an identifier - as they suggest, the identifier can be your project's URL but it isn't actually used. 

![Shows the Create API form from Auth0's web interface](/media/new-api.png "Create API")

Next, get the details of the API and Application that's been created. Go to Applications, open the menu next to the application you've created and open "settings". You'll need to copy all of it, the domain, client ID and client secret.

Next some code. I won't go through setting up the project, check [the example repo](https://github.com/kipparker/fastapi-auth0) if you want details. We'll need an endpoint to secure, this will do:

```python

@app.get("/")
def get():
    return {"message": "This is private"}

```

Our endpoint will be secured by requiring a valid jwt token, which arrives in the request header:

```json
{"authorization": "Bearer <token>"
```

We need two parts to add authentication - something to validate the token, and a way of injecting the authorisation code into private endpoints using FastAPI's dependencies. First of all verification:


```python
import jwt

def verify_token(token: str, domain: str, audience: str) -> dict[str, Any]:
    """
    Use the pyjwt jwkclient to get a signing key, then decode the supplied token
    """
    jwks_client = jwt.PyJWKClient(f"https://{domain}/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=audience,
        issuer=f"https://{domain}/",
    )
```


The `verify_token` function takes the token along with the domain and audience values and decodes the token. Because we're using a third-party auth provider, we need two steps:
- Use PyJWKClient to get a signing key
- Decode the token using that signing key

For injecting into endpoints, we can use:

```python
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Function that is used to validate the token in the case that it requires it
    """
    try:
        verify_token(credentials.credentials, AUTH0_DOMAIN, AUTH0_AUDIENCE)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

`Depends(security)` checks we have the authorization header (you'll get an Unauthorised error if it's missing) and gives us access to the token as `credentials.credentials`. Any authentication errors will be `PyJWTError` errors, so we can catch those, and return the message to the API user if the token fails.

Now we add this to the endpoint to secure it:

```python
from fastapi import FastAPI, Depends

import auth

app = FastAPI()


@app.get("/", dependencies=[Depends(auth.has_access)])
def get():
    return {"message": "This is private"}
```

How about testing the endpoint? We can use the `requests` library to get a token, and add it to our authorization header:

```python
import requests

payload = {
    "client_id": "<CLIENT_ID>",
    "client_secret": "<CLIENT_SECRET>",
    "audience": "<AUDIENCE>",
    "grant_type": "client_credentials",
}
r = requests.post("https://<your-domain>.auth0.com/oauth/token", json=payload)
# Returns {'access_token': '<very-long-token>', 'expires_in': 86400, 'token_type': 'Bearer'}

auth_header = {"authorization": f"Bearer {r['access_token']}"}
r = requests.get("http://127.0.0.1:8000/", headers=auth_header)
print(r.json())
```

This is deliberately a bare minimum implementation. You will want to add features. More expressive error handling might be one thing.

If you're implementing machine to machine authorisation, you'll want to include some logic to reuse tokens until they expire, Auth0 rates are based on tokens requested.

You might want to add scope validations if you're using different permission levels, take a look here for a nudge in the right direction: https://auth0.com/docs/quickstart/backend/python/01-authorization#validate-scopes

Have a look at the repo for the full example: https://github.com/kipparker/fastapi-auth0

References:

- Auth0 Docs: Python API: Authorization https://auth0.com/docs/quickstart/backend/python/01-authorization
- Securing FastAPI with JWT Token-based Authentication https://testdriven.io/blog/fastapi-jwt-auth/