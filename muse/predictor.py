#!/usr/bin/env python3
"""
Interest Predictor — 实时预测兴趣标签数量变化对各维度的影响。
纯数学公式模型，不需要训练数据，不需要历史记录。

输出一个 5 维雷达图数据点，浏览器端实时渲染。
所有函数都是纯函数（pure function），浏览器 JS 可重写版本。
"""

import math

# ── 默认参数 ──────────────────────────────────────────────────────────

DEFAULT_PARAMS = {
    "daily_pool_size": 150,       # M: 每日内容池（百度50+微博50+B站50）
    "avg_match_rate": 0.08,       # p: 单个标签平均匹配率
    "overlap_coeff": 0.15,        # λ: 标签重叠系数（0=完全不重叠,1=完全重叠）
    "relevance_coeff": 0.10,      # μ: 相关度衰减系数
    "fatigue_coeff": 0.05,        # φ: 疲劳系数（信息增益衰减率）
    "embedding_dim": 256,         # d: 嵌入向量维度
    "bytes_per_float": 4,         # float32
    "time_per_item_per_tag_ms": 0.004,  # k: 每条每个标签评分时间(ms)
    "overhead_ms": 2.0,           # 固定开销(ms)
}


# ── 核心预测函数 ──────────────────────────────────────────────────────

def coverage(N: int, params: dict = None) -> float:
    """
    覆盖率: 至少被一个标签匹配到的内容比例。
    coverage(N) = 1 - e^{-λN}
    
    N=1  → ~8%
    N=5  → ~33%
    N=10 → ~55%
    N=20 → ~80%
    N=30 → ~92%
    """
    p = params or DEFAULT_PARAMS
    lam = p["avg_match_rate"] * (1 - p["overlap_coeff"])
    return 1 - math.exp(-lam * N)


def marginal_coverage(N: int, params: dict = None) -> float:
    """
    第 N 个标签的边际覆盖率增益。
    d(coverage)/dN = λe^{-λN}
    """
    p = params or DEFAULT_PARAMS
    lam = p["avg_match_rate"] * (1 - p["overlap_coeff"])
    return lam * math.exp(-lam * N)


def daily_items(N: int, params: dict = None) -> int:
    """每日推荐项总数 = M × coverage(N)"""
    p = params or DEFAULT_PARAMS
    return int(p["daily_pool_size"] * coverage(N, p))


def avg_relevance(N: int, params: dict = None) -> float:
    """
    平均相关度评分（0~1）。
    随标签增多而提升，但呈饱和趋势。
    relevance(N) = 1 - e^{-μN}
    """
    p = params or DEFAULT_PARAMS
    mu = p["relevance_coeff"]
    return 1 - math.exp(-mu * N)


def info_gain(N: int, params: dict = None) -> float:
    """
    每条推荐的信息增益（bits）。
    先增后减：太少标签覆盖率低，太多标签推荐新鲜度下降（疲劳效应）。
    
    info_gain(N) = coverage(N) × relevance(N) × e^{-φN}
    
    φ = 疲劳系数（默认 0.05）。
    物理含义：每增加一个标签，推荐的新鲜度因"已看过相似内容"而衰减。
    
    N=5  → 中等
    N=10 → 峰值附近
    N=20 → 开始下降
    N=30 → 显著下降
    """
    p = params or DEFAULT_PARAMS
    c = coverage(N, p)
    r = avg_relevance(N, p)
    fatigue = p.get("fatigue_coeff", 0.05)
    return c * r * math.exp(-fatigue * N)


def memory_kb(N: int, params: dict = None) -> float:
    """内存占用 (KB) = N × d × 4 bytes"""
    p = params or DEFAULT_PARAMS
    return N * p["embedding_dim"] * p["bytes_per_float"] / 1024


def processing_time_ms(N: int, params: dict = None) -> float:
    """处理时间 (ms) = k × N × M + 固定开销"""
    p = params or DEFAULT_PARAMS
    return p["time_per_item_per_tag_ms"] * N * p["daily_pool_size"] + p["overhead_ms"]


# ── 雷达图数据 ────────────────────────────────────────────────────────

def radar_data(N: int, params: dict = None) -> dict:
    """返回 5 维雷达图的完整数据点。"""
    return {
        "N": N,
        "coverage_pct": round(coverage(N, params) * 100, 1),
        "avg_relevance": round(avg_relevance(N, params), 3),
        "info_gain_bits": round(info_gain(N, params), 3),
        "daily_items": daily_items(N, params),
        "memory_kb": round(memory_kb(N, params), 1),
        "processing_time_ms": round(processing_time_ms(N, params), 1),
        "marginal_gain_pct": round(marginal_coverage(N, params) * 100, 2),
        "_formulas": {
            "coverage": "1 - e^{-λN}",
            "relevance": "1 - e^{-μN}",
            "info_gain": "cov(N) × rel(N) × (1 - overlap)",
            "memory": "N × d × 4 bytes",
            "time": "k × N × M + overhead"
        }
    }


def radar_series(max_N: int = 30, params: dict = None) -> list:
    """返回 N=1 到 max_N 的序列数据。"""
    return [radar_data(N, params) for N in range(1, max_N + 1)]


def suggest_optimal_N(params: dict = None) -> dict:
    """
    推荐最优标签数：信息增益与计算成本的收益交叉点。
    返回多个候选点供用户决策。
    """
    p = params or DEFAULT_PARAMS
    series = radar_series(30, p)
    
    # 找信息增益峰值
    ig_max = max(series, key=lambda x: x["info_gain_bits"])
    
    # 找边际收益 < 0.5% 的点（再增加也没意义）
    marginal_threshold = 0.5  # 0.5%
    sweet_spot = 1
    for s in series:
        if s["marginal_gain_pct"] > marginal_threshold:
            sweet_spot = s["N"]
    
    # 找覆盖率 > 60% 的最小 N
    coverage_60 = next((s["N"] for s in series if s["coverage_pct"] >= 60), 30)
    
    return {
        "info_gain_peak_N": ig_max["N"],
        "info_gain_peak_value": ig_max["info_gain_bits"],
        "sweet_spot_N": sweet_spot,  # 边际收益 > 0.5% 的最后一个
        "coverage_60_N": coverage_60,
        "recommendation": (
            f"推荐 10-15 个标签（信息增益峰值在 ~{ig_max['N']}，"
            f"边际收益在 ~{sweet_spot} 后低于 0.5%/tag）"
        )
    }


# ── 演示 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Interest Predictor — 数学预测模型")
    print("=" * 60)
    print()
    
    print("关键参数：")
    for k, v in DEFAULT_PARAMS.items():
        print(f"  {k}: {v}")
    print()
    
    # 推荐
    opt = suggest_optimal_N()
    print("推荐结果：")
    for k, v in opt.items():
        print(f"  {k}: {v}")
    print()
    
    # 关键点
    print("关键数据点：")
    for N in [1, 3, 5, 10, 15, 20, 30]:
        d = radar_data(N)
        print(f"  N={N:2d}: coverage={d['coverage_pct']:5.1f}%  "
              f"relevance={d['avg_relevance']:.3f}  "
              f"info_gain={d['info_gain_bits']:.3f}  "
              f"items={d['daily_items']:3d}  "
              f"mem={d['memory_kb']:5.1f}KB  "
              f"time={d['processing_time_ms']:5.1f}ms  "
              f"边际={d['marginal_gain_pct']:.2f}%")
    print()
    
    # 完整序列（方便绘图）
    print("雷达图时序数据 (N=1~30)：")
    series = radar_series(30)
    print(f"  共 {len(series)} 个数据点")
    print(f"  信息增益峰值: N={max(series, key=lambda x: x['info_gain_bits'])['N']}")
