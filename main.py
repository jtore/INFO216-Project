from fastapi import FastAPI, Form

app = FastAPI()


@app.get("/query")
async def query(query_string: str = Form(...)):
    return {query_string}