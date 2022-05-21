# Fast API with Auth0

A very simple example of using Auth0 with FastAPI

## Running locally

Copy .env.template to a .env and replace the values with the values from the Auth0 API you have created. Then:

```
pipenv install --dev
pipenv run uvicorn main:app --reload --debug
```

To make a test request (with the local server running):

```
pipenv run python client.py
```