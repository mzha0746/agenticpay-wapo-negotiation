# AgenticPay：模拟 Bezos 收购华盛顿邮报

参照 AgenticPay 论文（arXiv 2602.06008）的单买家 / 单卖家设置，用 Qwen3-4B-Instruct-2507 离线模拟 Jeff Bezos（买家，保密上限 3.5 亿美元）向 Donald Graham（卖家，保密底线 2 亿美元）收购华盛顿邮报的谈判。

完整报告见 **[REPORT_zh.md](REPORT_zh.md)**（PDF 版：`REPORT_zh.pdf`；英文版：`REPORT.md`）。

## 主要结果（每组 10 次）

| 条件 | 成交率 | 平均成交价（百万美元） | 平均轮数 |
|---|---|---|---|
| 加入人物资料，原版买家 prompt（基准） | 40% | 331.2 | 18.0 |
| 买家变体 A：低价锚定 + 数据论证 + 越让越少 | 40% | 231.2 | 16.7 |
| 买家变体 B：按轮次固定让步 + 非价格条件交换 | 80% | 214.1 | 11.7 |

## 文件说明

```
src/facts.py             加入 prompt 的公开事实及其来源
src/prompts.py           论文 Table 14/15 原文 prompt、人物背景、买家策略变体
src/negotiate.py         1 买家 × 1 卖家 × 1 商品的谈判循环（AgenticPay Task1 规则）和实验运行器
src/analyze.py           汇总表 -> results/summary.md、results/summary.json
src/check_schedule.py    诊断：变体 B 是否按让步时间表出价
src/offer_violations.py  诊断：越过保留价的报价
src/md2pdf.py            把报告转成 PDF
results/                 每次运行一个 JSON（完整对话、结果、种子、采样参数）
results_rounds8/         稳健性检验：最多 8 轮
results_temp0/           稳健性检验：温度 0
```

## 运行环境

- Python 3.10+，依赖 `requests`（`pip install -r requirements.txt`）
- 一个 OpenAI 兼容的模型服务，二选一：
  - llama.cpp：`llama-server -m Qwen3-4B-Instruct-2507-Q8_0.gguf -ngl 99 -c 12288 --port 8080`
  - vLLM：`vllm serve Qwen/Qwen3-4B-Instruct-2507 --port 8080`

## 复现

```bash
cd src
python negotiate.py --runs 10 --out ../results   # 可断点续跑
python analyze.py ../results
```
