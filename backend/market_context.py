import gateio_api

def get_general_market_summary():
    pairs = ["BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT"]
    lines = ["📊 *Ringkasan Pasar*"]
    for pair in pairs:
        ticker = gateio_api.get_ticker(pair)
        if ticker and isinstance(ticker, list) and len(ticker) > 0:
            t = ticker[0]
            last = t.get('last', 'N/A')
            change = t.get('change_percentage', '0')
            change_display = f"+{change}%" if float(change) > 0 else f"{change}%"
            pair_display = pair.replace('_', '/')
            lines.append(f"• {pair_display}: ${last} ({change_display})")
        else:
            lines.append(f"• {pair.replace('_', '/')}: Data tidak tersedia")
    return "\n".join(lines)

def get_price_context(symbol):
    pair = f"{symbol}_USDT"
    ticker = gateio_api.get_ticker(pair)
    if ticker and isinstance(ticker, list) and len(ticker) > 0:
        t = ticker[0]
        last = t.get('last', 'N/A')
        change = t.get('change_percentage', '0')
        change_display = f"+{change}%" if float(change) > 0 else f"{change}%"
        pair_display = pair.replace('_', '/')
        return f"Harga {pair_display}: ${last} (24j: {change_display})"
    return None

def get_orderbook_context(symbol):
    pair = f"{symbol}_USDT"
    ob = gateio_api.get_order_book(pair, limit=3)
    if 'bids' in ob and 'asks' in ob and ob['bids'] and ob['asks']:
        bids = ob['bids'][:3]
        asks = ob['asks'][:3]
        lines = [f"📚 Order Book {pair.replace('_', '/')}:"]
        lines.append("🔵 *Bids (Beli)*")
        for bid in bids:
            lines.append(f"   {bid[0]} — {bid[1]}")
        lines.append("🔴 *Asks (Jual)*")
        for ask in asks:
            lines.append(f"   {ask[0]} — {ask[1]}")
        return "\n".join(lines)
    return None