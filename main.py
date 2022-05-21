from fastapi import FastAPI, Depends

import auth

app = FastAPI()


@app.get("/", dependencies=[Depends(auth.has_access)])
def get():
    return {"message": "This is private"}
