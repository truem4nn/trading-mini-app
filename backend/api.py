from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import gateio_api
import market_context
import deepseek_ai
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: int
    history: Optional[List[dict]] = []

@app.get("/api/ticker/{pair}")
async def get_ticker(pair: str):
    data = gateio_api.get_ticker(pair)
    if not data:
        raise HTTPException(status_code=404, detail="Pair not found")
    return data

@app.get("/api/orderbook/{pair}")
async def get_orderbook(pair: str, limit: int = 10):
    return gateio_api.get_order_book(pair, limit)

@app.get("/api/market/summary")
async def market_summary():
    pairs = ["BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT"]
    result = {}
    for pair in pairs:
        data = gateio_api.get_ticker(pair)
        if data and len(data) > 0:
            result[pair] = data[0]
    return result

@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Deteksi konteks sederhana
    context = ""
    lower = req.message.lower()
    if "btc" in lower:
        ctx = market_context.get_price_context("BTC")
        if ctx:
            context = ctx
    elif "eth" in lower:
        ctx = market_context.get_price_context("ETH")
        if ctx:
            context = ctx
    else:
        context = market_context.get_general_market_summary()
    
    messages = req.history + [{"role": "user", "content": req.message}]
    response = deepseek_ai.chat_with_ai(messages, market_context=context)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)