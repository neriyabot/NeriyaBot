def position_size_from_risk(balance_usdt: float, risk_pct: float, entry: float, stop: float) -> float:
    risk_usdt = balance_usdt * (risk_pct / 100.0)
    distance = abs(entry - stop)
    if distance <= 0:
        return 0.0
    qty_base = risk_usdt / distance
    return max(qty_base, 0.0)

def hit_daily_loss_limit(start_equity: float, current_equity: float, max_daily_loss_pct: float) -> bool:
    if start_equity <= 0:
        return False
    dd_pct = 100.0 * (start_equity - current_equity) / start_equity
    return dd_pct >= max_daily_loss_pct