from fastapi import FastAPI
from pydantic import BaseModel

from .db import get_client

app = FastAPI(title="Mafia Certificate Redeem Code API")


class RedeemRequest(BaseModel):
    code: str


class RedeemResponse(BaseModel):
    valid: bool
    used: bool = False
    reward: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/redeem", response_model=RedeemResponse)
def redeem(req: RedeemRequest):
    code = req.code.strip()
    if not code:
        return RedeemResponse(valid=False)

    client = get_client()
    result = (
        client.table("codes")
        .select("*")
        .eq("code", code)
        .limit(1)
        .execute()
    )

    if not result.data:
        return RedeemResponse(valid=False)

    row = result.data[0]

    if not row.get("active", True):
        return RedeemResponse(valid=True, used=True)

    reward = {
        "type": row.get("type"),
        "variable": row.get("variable"),
        "screen": row.get("screen"),
        "amount": row.get("amount"),
    }
    extra = row.get("value") or {}
    reward.update(extra)

    return RedeemResponse(valid=True, used=False, reward=reward)
