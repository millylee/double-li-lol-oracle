# Li²-LoLOracle（双Li · 峡谷先知）`double-li-lol-oracle`

> Predict the Rift, before the Rift. —— 出品：**Li²**（双Li / double-li）· LoL S1–S16 全球赛事数据管线与多智能体胜负预测系统

涵盖 **英雄联盟 S1 (2011) 至 S16 (2026)** 全部全球总决赛 (Worlds)、季中冠军赛 (MSI) 以及 **四大赛区 (LCK / LPL / LEC / LCS)** 核心赛事数据，提供 **跨赛区动态 Elo 评级 + 机器学习与马尔可夫链系列赛模拟 + 多角色 Agent 协同胜负预测**。

## 快速启动

### 1. 初始化 S1–S16 历史数据库与 Elo 模型
```bash
python scripts/sync_data.py
```

### 2. 运行历届世界赛/MSI 回测与 Agent 预测演示
```bash
python scripts/run_backtest.py
```

### 3. 启动可视化 Web 预测工作台
```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
浏览器访问 `http://127.0.0.1:8000` 即可使用：
- **⚡ Agent 对阵胜负预测台**：支持任意两支战队在 BO1 / BO3 / BO5 下的胜率推演、比分概率分布、五路首发对位、BP 重叠英雄池、因子归因与多智能体推理轨迹。
- **🏆 S1–S16 全球赛事编年史**：按赛季 (S1–S16)、级别 (Worlds / MSI / 四大赛区) 浏览历届赛事、FMVP 与淘汰赛/常规赛比分，并支持一键导入 AI 复盘推演。
- **📊 跨赛区 Elo 战力榜 & 历史回测**：查看战队历史更名谱系（如 `SK Telecom T1 → T1`、`Samsung White/Galaxy → Gen.G`）继承后的动态战力排行，以及在线调用 Leaguepedia Cargo API 同步最新比赛。
