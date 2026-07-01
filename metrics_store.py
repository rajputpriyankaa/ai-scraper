def update_metrics(key):
    metrics_dic[key] += 1

def add_latency(ms: float):
    metrics_dic["total_latency_ms"] += ms

def update_strategy(strategy):
    if strategy in metrics_dic["strategy_breakdown"]:
        metrics_dic["strategy_breakdown"][strategy] += 1

metrics_dic = {
    "total_requests": 0,
    "success_count": 0,
    "total_latency_ms": 0,
    "strategy_breakdown": {
        "requests_ok": 0,
        "playwright_dom": 0,
        "playwright_network": 0
    },
    "total_ai_calls": 0
}