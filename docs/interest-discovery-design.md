# 每日情报系统 — 交互式兴趣发现 + 实时预测仪表盘

## 接续 `docs/daily-intelligence-plan.md` 的 Level 2 设计
> Date: 2026-05-14 | Author: Pixie (CTO)

---

## 一、问题：冷启动 + 学习速率

当前 Level 2 设计的局限：

```
每天推送 2 次（5:30am/pm）
每次你做 2 次 binary choice（👍/👎）
每天 info gain = 4 bits
冷启动需要数十天才能收敛到稳定偏好
```

这是**纯被动学习**——系统只能从你的点击中推断偏好，而你只能在已有的推荐里选。

Reddit/Pinterest 的做法不一样：**第一次注册就主动问你兴趣**，让你直接告诉系统你是谁。

---

## 二、交互式兴趣发现（冷启动模块）

### 首次使用流程

```
Step 0：系统初始化
  │ 显示 10 个通用兴趣标签（General Tags）
  ▼
Step 1：你选至少 3 个
  │ [AI/ML]  [设计工具]  [创业]  [学术论文]  [音乐]  [游戏]
  │ [财经]    [科技新闻]  [开源]   [AI 艺术]
  ▼
Step 2：点击某个标签 → 展开 10 个子兴趣
  │ AI/ML ──→ [深度学习] [LLM] [多模态] [扩散模型]
  │            [Agent]    [RAG]  [RL]     [推理]
  │            [训练框架]  [评估基准]
  ▼
Step 3：(可选) 继续点击子兴趣 → 再下一层
  │ 多模态 ──→ [CLIP] [BLIP] [LLaVA] [Qwen-VL]
  │            [Video Understanding] [Cross-modal Retrieval]
  ▼
Step 4：你确认选择 → 系统立即生成初始兴趣向量 → 进入每日推送
```

### 树状兴趣标签库（预定义，~500 个节点）

```
interests/
├── root.json              ← 10 个一级标签 + 元数据
├── ai-ml.json             ← AI/ML 子标签
├── design-tools.json      ← 设计工具子标签
├── startup.json           ← 创业子标签
├── academic.json          ← 学术论文子标签
└── ...
```

### 与学习系统的关系

```
冷启动（你主动选）
  │ 生成初始兴趣向量（粗粒度）
  ▼
每日推送（被动学习）
  │ 你点 👍/👃 → 兴趣向量微调（细粒度）
  ▼
你主动重新进入兴趣选择
  │ 添加/删除标签 → 手动调整向量
  ▼
系统持续收敛
```

**这不是非此即彼——冷启动 → 被动学习 → 再主动微调，三阶段循环。**

---

## 三、实时预测仪表盘（数学公式模型）

### 核心问题

用户在添加兴趣标签时，需要一个**可视化 trade-off**，不是盲目叠加：

| 更多标签的好处 | 更多标签的代价 |
|--------------|-------------|
| ✅ 覆盖更广的内容 | ❌ 每个标签匹配到的内容变少 |
| ✅ 推荐更精准 | ❌ 计算量线性增长 |
| ✅ 不会错过冷门兴趣 | ❌ 边际信息增益递减 |

### 数学模型

定义变量：
- **N** = 兴趣标签数量（用户当前选的）
- **M** = 每日内容池大小（Baidu 50 + Weibo 50 + Bilibili 50 = ~150）
- **p** = 平均匹配率（一个标签匹配内容池的比例，约 0.08）
- **λ** = 标签间的重叠系数（0 = 完全不重叠, 1 = 完全重叠）

#### 1. 覆盖率 prediction

```
coverage(N) = 1 - e^{-λN}
              
N=1  → 约 8% 内容被覆盖
N=5  → 约 33% （practical zone）
N=10 → 约 55%
N=20 → 约 80%
N=30 → 约 92% （边际收益极低）
```

**边际收益 = coverage(N) - coverage(N-1) ≈ λe^{-λN}**

第一条 tag 带来 8% 覆盖，第 20 条只带来 1.2%。

#### 2. 信息增益（Info Gain per recommendation）

```
info_gain(N) = H₀ - H(N)
             
H₀ = log₂(M)           ← 等概率随机推荐的熵
H(N) = Σ P(item|N) · log₂(1/P(item|N))  ← 有标签后的条件熵
```

简化模型：
```
info_gain_ratio(N) = coverage(N) × relevance(N)
                   = (1 - e^{-λN}) × (1 - e^{-μN})
```

这是一个**先增后减的曲线**——太少标签覆盖率低，太多标签每条推荐的新鲜度下降。

**最优标签数 ≈ 10-15**（从信息论角度看）。

#### 3. 计算复杂度

```
time(N) = O(N × M) = k × N × M
memory(N) = O(N × d) ≈ N × 256 × 4 bytes ≈ 1KB × N
```

- 时间线性增长：N=5 时 5ms，N=30 时 30ms（MacBook M 系列）
- 内存几乎可忽略：30 个标签 × 256 维向量 × 4 字节 = 30KB

#### 4. 每日推荐项总数

```
daily_items(N) = M × coverage(N)
               = 150 × (1 - e^{-λN})
```

- N=3: ~34 条/天
- N=10: ~83 条/天
- N=20: ~120 条/天

### 雷达图（5 维度）

```
                覆盖率 (%)
                  ↑
                  │  ◈
        计算时间   │    ◈   信息增益
         (ms)     │      ◈   (bits/rec)
                  │
                  ├─── ◈ ──→
                  │
                每日推荐    内存占用
                 条数        (KB)
```

### 交互式反馈

当用户 hover 添加新 tag 时，雷达图**实时变化**：

```
你 hover "+多模态" → 雷达图立即显示：
  ┌─ 覆盖率从 33% → 42%   (+9%)
  ├─ 信息增益从 0.8 → 0.72 (-0.08 bits)
  ├─ 每日推荐从 50 → 63    (+13条)
  ├─ 时间从 8ms → 10ms     (+2ms)
  └─ 内存从 12KB → 13KB    (+0.1KB)

你看到边际收益下降，决定不加了。
```

**全部用公式实时计算，不需要训练，不需要存储历史数据。**
在浏览器端用 JS 就能跑。

---

## 四、工程结构

```
/Volumes/Lab/Aether/swarm/
├── intelligence/
│   ├── __init__.py
│   ├── interest_engine.py        ← 兴趣向量 & 相似度计算
│   ├── daily_briefing.py         ← 每日情报生成管道
│   ├── feedback.py               ← 👍/👎 反馈学习
│   ├── tag_tree.py               ← 兴趣标签树（~500 节点）
│   ├── tag_tree/                 ← 标签树 JSON 文件
│   │   ├── root.json
│   │   ├── ai-ml.json
│   │   ├── design-tools.json
│   │   └── ...
│   ├── predictor.py              ← 雷达图数学模型
│   ├── onboarding.py             ← 冷启动交互逻辑
│   └── profile.json              ← 运行时兴趣配置
├── dashboard/
│   ├── hierarchy.html            ← 已有
│   └── interests.html            ← 兴趣雷达图 + 标签选择 UI
├── scripts/
│   ├── run_daily_briefing.py     ← cron 入口
│   └── register_intel_cron.sh    ← 注册 5:30am/pm
└── docs/
    ├── daily-intelligence-plan.md
    ├── open-source-analysis.md
    └── interest-discovery-design.md  ← 本文档
```

---

## 五、工作量估算

| 模块 | 文件/改动 | 预估行数 | 预估时间 |
|------|----------|---------|---------|
| 标签树数据 | `tag_tree/*.json` | ~200 | 30min（一次编写） |
| 标签树加载 & 交互 | `tag_tree.py` | ~60 | 15min |
| 数学模型 | `predictor.py` | ~50 | 15min |
| 冷启动流程 | `onboarding.py` | ~80 | 20min |
| 雷达图 UI | `dashboard/interests.html` (单文件) | ~300 | 45min |
| 集成到 Orchestrator | 加 2 个 API endpoint | ~20 | 5min |
| cron 注册 | `register_intel_cron.sh` | ~30 | 5min |
| **总计** | | **~740** | **~2h** |

---

## 六、关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 标签树用什么数据结构 | 嵌套 JSON（不是数据库） | 500 个标签，静态数据，flat JSON 足够 |
| 雷达图在哪里渲染 | 浏览器端 JS | 无需后端计算，hover 即时响应 |
| 数学模型用什么 | 纯函数（没有 ML） | 覆盖率和信息增益有 closed-form 公式，不需要学习 |
| 冷启动和每日推送的关系 | 独立模块 | 冷启动只用一次，每日推送长期运行 |
| 标签数限制 | 不限制，但雷达图告诉你何时停止 | 用户自主决策，不是系统强制的 |
