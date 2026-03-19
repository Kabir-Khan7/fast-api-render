"""
PSX Intelligence Engine
- Stock classification: Blue Chip / Growth / Value / Income / Speculative / Penny
- Sector benchmarking vs PSX industry averages
- Buy / Hold / Sell signal generation
"""
from typing import Optional, Dict, List

PSX_SECTOR = {
    "Banking":    {"avg_pe":6.5,"avg_pb":1.2,"avg_div":8.5,"avg_roe":18,"avg_pm":28,"avg_vol":1.8,
                   "peers":["HBL","MCB","UBL","BAHL","MEBL","NBP","ABL","BAFL"]},
    "Energy":     {"avg_pe":7.0,"avg_pb":1.5,"avg_div":7.0,"avg_roe":22,"avg_pm":18,"avg_vol":2.1,
                   "peers":["OGDC","PPL","PSO","MARI","POL"]},
    "Cement":     {"avg_pe":8.5,"avg_pb":1.8,"avg_div":3.5,"avg_roe":14,"avg_pm":12,"avg_vol":2.4,
                   "peers":["LUCK","DGKC","MLCF","CHCC","PIOC"]},
    "Fertilizer": {"avg_pe":7.8,"avg_pb":2.1,"avg_div":9.0,"avg_roe":28,"avg_pm":22,"avg_vol":1.9,
                   "peers":["ENGRO","EFERT","FFC","FATIMA","FFBL"]},
    "Power":      {"avg_pe":6.0,"avg_pb":1.0,"avg_div":10.0,"avg_roe":16,"avg_pm":14,"avg_vol":1.6,
                   "peers":["HUBC","KAPCO","NCPL","KEL","PKGP"]},
    "Technology": {"avg_pe":18.0,"avg_pb":3.5,"avg_div":2.5,"avg_roe":25,"avg_pm":15,"avg_vol":3.2,
                   "peers":["SYS","TRG","NETSOL","AVN","HUMNL"]},
    "Pharma":     {"avg_pe":12.0,"avg_pb":2.8,"avg_div":4.0,"avg_roe":20,"avg_pm":10,"avg_vol":2.0,
                   "peers":["SEARL","HINOON","FEROZ","GLAXO","AGP"]},
    "Textile":    {"avg_pe":5.5,"avg_pb":0.9,"avg_div":5.5,"avg_roe":12,"avg_pm":8,"avg_vol":2.8,
                   "peers":["NCL","GATM","KTML","GADT","CRTM"]},
    "Consumer":   {"avg_pe":22.0,"avg_pb":5.0,"avg_div":3.0,"avg_roe":30,"avg_pm":12,"avg_vol":1.7,
                   "peers":["NESTLE","COLG","UNILEVER","UNITY","QUICE"]},
    "N/A":        {"avg_pe":9.0,"avg_pb":1.8,"avg_div":5.0,"avg_roe":16,"avg_pm":12,"avg_vol":2.2,
                   "peers":[]},
}
PSX_MKT = {"pe":8.5,"pb":1.6,"div":6.2,"roe":18.0,"pm":14.0,"vol":2.1}


def classify_stock(symbol, price, market_cap, pe, pb, div_yield, roe, vol, sector="N/A"):
    bench = PSX_SECTOR.get(sector, PSX_SECTOR["N/A"])
    sc = {"blue_chip":0,"growth":0,"value":0,"income":0,"speculative":0,"penny":0}

    if price < 10:                      sc["penny"] += 4
    elif price < 25:                    sc["penny"] += 2
    if market_cap and market_cap < 1e9: sc["penny"] += 2

    if market_cap and market_cap > 100e9: sc["blue_chip"] += 3
    elif market_cap and market_cap > 50e9: sc["blue_chip"] += 2
    if vol and vol < 1.8:               sc["blue_chip"] += 2
    if div_yield and div_yield > 5:     sc["blue_chip"] += 1
    if roe and roe > 15:                sc["blue_chip"] += 1
    if pe and 4 < pe < 12:             sc["blue_chip"] += 1

    if roe and roe > 22:                sc["growth"] += 3
    if pe and pe > 14:                  sc["growth"] += 2
    if div_yield and div_yield < 2:     sc["growth"] += 1

    if pe and pe < bench["avg_pe"] * 0.65: sc["value"] += 4
    elif pe and pe < bench["avg_pe"] * 0.85: sc["value"] += 2
    if pb and pb < 1.0:                 sc["value"] += 3
    elif pb and pb < 1.3:               sc["value"] += 1

    if div_yield and div_yield > 9:     sc["income"] += 4
    elif div_yield and div_yield > 7:   sc["income"] += 3
    elif div_yield and div_yield > 5:   sc["income"] += 2

    if vol and vol > 3.5:               sc["speculative"] += 3
    if not pe or pe > 30:               sc["speculative"] += 1
    if market_cap and market_cap < 5e9: sc["speculative"] += 1

    if sc["penny"] >= 4:
        cat, color, icon = "Penny Stock",  "#f97316", "⚠"
    elif sc["blue_chip"] >= 5:
        cat, color, icon = "Blue Chip",    "#38bdf8", "★"
    elif sc["growth"] >= 4:
        cat, color, icon = "Growth",       "#a78bfa", "▲"
    elif sc["value"] >= 3:
        cat, color, icon = "Value",        "#22c55e", "◆"
    elif sc["income"] >= 3:
        cat, color, icon = "Income",       "#f59e0b", "₨"
    elif sc["speculative"] >= 3:
        cat, color, icon = "Speculative",  "#ef4444", "!"
    else:
        cat, color, icon = "General",      "#94a3b8", "—"

    descs = {
        "Blue Chip":   "Large, established company. Stable earnings, consistent dividends, lower risk.",
        "Growth":      "High ROE, reinvests profits. Higher P/E justified by growth premium.",
        "Value":       "Trading below intrinsic value on P/E and P/B. Classic buy-cheap strategy.",
        "Income":      "High dividend yield — ideal for regular cash income from your investment.",
        "Speculative": "High volatility, limited fundamentals. Experienced traders only.",
        "Penny Stock": "Low-priced, small market cap. Very high risk, high reward potential.",
        "General":     "Balanced characteristics — no dominant category.",
    }
    secondary = []
    if cat != "Income"   and sc["income"] >= 2:     secondary.append("High Dividend")
    if cat != "Value"    and sc["value"] >= 2:      secondary.append("Undervalued")
    if cat != "Blue Chip" and sc["blue_chip"] >= 3: secondary.append("Blue Chip Traits")

    return {"primary":cat,"color":color,"icon":icon,"secondary":secondary,
            "description":descs.get(cat,""),"scores":sc}


def benchmark_vs_sector(sector, pe, pb, div_yield, roe, profit_margin, vol):
    bench = PSX_SECTOR.get(sector, PSX_SECTOR["N/A"])

    def cmp(val, avg, lower_better=False):
        if val is None or not avg:
            return {"value":None,"avg":avg,"pct_diff":None,"rating":"N/A"}
        pct = ((val - avg) / avg) * 100
        if lower_better:
            rating = "better" if val < avg*0.9 else "worse" if val > avg*1.1 else "in-line"
        else:
            rating = "better" if val > avg*1.1 else "worse" if val < avg*0.9 else "in-line"
        return {"value":round(val,2),"avg":round(avg,2),
                "pct_diff":round(pct,1),"rating":rating}

    comps = {
        "P/E Ratio":      cmp(pe,          bench["avg_pe"],  lower_better=True),
        "P/B Ratio":      cmp(pb,          bench["avg_pb"],  lower_better=True),
        "Dividend Yield": cmp(div_yield,   bench["avg_div"]),
        "ROE":            cmp(roe,         bench["avg_roe"]),
        "Profit Margin":  cmp(profit_margin, bench["avg_pm"]),
        "Volatility":     cmp(vol,         bench["avg_vol"], lower_better=True),
    }
    better = sum(1 for v in comps.values() if v["rating"]=="better")
    worse  = sum(1 for v in comps.values() if v["rating"]=="worse")
    total  = better + worse
    rating = "outperformer" if total>0 and better>=total*0.65 else \
             "underperformer" if total>0 and worse>=total*0.65 else "in-line"
    return {"sector":sector,"peers":bench["peers"],"comparisons":comps,
            "sector_rating":rating,"better":better,"worse":worse}


def generate_signal(score, rsi, macd_cross, ma_trend, momentum, vol_level,
                    adx_strength, adx_dir, w52_zone, boll_pos,
                    pe, div_yield, sector, above_vwap, obv_conf):
    bull, bear, notes = [], [], []

    if rsi is not None:
        if rsi < 30:   bull.append(f"RSI oversold ({rsi:.1f}) — bounce zone")
        elif rsi > 70: bear.append(f"RSI overbought ({rsi:.1f}) — pullback risk")
        elif rsi > 55: bull.append(f"RSI {rsi:.1f} — positive momentum")
        else:          notes.append(f"RSI {rsi:.1f} — neutral")

    macd_map = {"bullish_crossover": (bull, "MACD bullish crossover — new uptrend signal"),
                "bearish_crossover": (bear, "MACD bearish crossover — new downtrend signal"),
                "bullish":           (bull, "MACD positive — upward momentum active"),
                "bearish":           (bear, "MACD negative — downward momentum active")}
    if macd_cross in macd_map:
        lst, msg = macd_map[macd_cross]; lst.append(msg)

    if "bullish" in ma_trend:   bull.append(f"MA trend: {ma_trend.replace('_',' ')} — price above averages")
    elif "bearish" in ma_trend: bear.append(f"MA trend: {ma_trend.replace('_',' ')} — price below averages")

    if w52_zone == "near_highs": bull.append("Trading near 52W highs — strong price momentum")
    elif w52_zone == "near_lows": bear.append("Trading near 52W lows — weak price action")

    if boll_pos == "near_lower": bull.append("Near Bollinger lower band — mean reversion buy signal")
    elif boll_pos == "near_upper": bear.append("Near Bollinger upper band — mean reversion sell signal")

    if above_vwap is True:  bull.append("Price above VWAP — bullish institutional positioning")
    elif above_vwap is False: bear.append("Price below VWAP — bearish institutional positioning")

    if obv_conf == "confirmed" and len(bull) > len(bear): bull.append("OBV confirms buying pressure")
    elif obv_conf == "divergence": bear.append("OBV divergence — volume does not support rally ⚠")
    elif obv_conf == "bullish_divergence": bull.append("OBV bullish divergence — possible accumulation")

    if "strong_positive" in momentum or "positive" in momentum: bull.append(f"Momentum: {momentum.replace('_',' ')}")
    elif "negative" in momentum: bear.append(f"Momentum: {momentum.replace('_',' ')}")

    if adx_strength in ("strong","very_strong") and adx_dir == "up":   bull.append(f"ADX {adx_strength.replace('_',' ')} uptrend")
    elif adx_strength in ("strong","very_strong") and adx_dir == "down": bear.append(f"ADX {adx_strength.replace('_',' ')} downtrend")

    bench = PSX_SECTOR.get(sector, PSX_SECTOR["N/A"])
    if pe and pe < bench["avg_pe"] * 0.7:
        bull.append(f"P/E {pe:.1f}x — well below sector avg ({bench['avg_pe']}x)")
    elif pe and pe > bench["avg_pe"] * 1.6:
        bear.append(f"P/E {pe:.1f}x — premium valuation vs sector ({bench['avg_pe']}x)")
    if div_yield and div_yield > bench["avg_div"] * 1.2:
        bull.append(f"Dividend {div_yield:.1f}% — above sector avg ({bench['avg_div']}%)")

    if vol_level in ("high","very_high"):
        notes.append(f"{vol_level.replace('_',' ').title()} volatility — size positions carefully")

    if score >= 68 and len(bull) > len(bear):
        action, ac, ab = "BUY",          "#22c55e", "rgba(34,197,94,0.10)"
        conf = "High" if score >= 76 else "Moderate"
        reason = f"Score {score:.0f}/100 with {len(bull)} bullish and {len(bear)} bearish signals — upward technical bias."
    elif score <= 35 or len(bear) > len(bull) * 1.5:
        action, ac, ab = "SELL / REDUCE", "#ef4444", "rgba(239,68,68,0.10)"
        conf = "High" if score <= 28 else "Moderate"
        reason = f"Score {score:.0f}/100 with {len(bear)} bearish signals — technical weakness, consider reducing."
    else:
        action, ac, ab = "HOLD / WATCH", "#f59e0b", "rgba(245,158,11,0.10)"
        conf = "Moderate" if 44 <= score <= 60 else "Low"
        reason = f"Score {score:.0f}/100 — mixed signals. Wait for a clearer technical setup."

    return {"action":action,"action_color":ac,"action_bg":ab,"confidence":conf,
            "score":score,"bull":bull,"bear":bear,"notes":notes,"reasoning":reason,
            "disclaimer":"Educational signal only. Not financial advice. Always do your own research before investing."}