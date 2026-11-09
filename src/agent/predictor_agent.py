import json
import time
from typing import Any, Dict, List, Optional
from pathlib import Path
from src.config import DB_PATH, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from src.agent.tools import AgentToolbox
from src.agent.prompts import SYSTEM_CHIEF_PREDICTOR_PROMPT
from src.analytics.timeline_simulator import MatchTimelineSimulator


class MultiAgentMatchPredictor:
    """
    Orchestrates 3 specialized analytical sub-agents + 1 Chief Predictor Agent:
    - Agent 1 (Quant & Macro Analyst): Executes `tool_quant_baseline_and_pace`
    - Agent 2 (History & Pedigree Analyst): Executes `tool_h2h_and_pedigree`
    - Agent 3 (Draft & Lane Tactician): Executes `tool_roster_and_bp_clash`
    - Chief Predictor Agent: Synthesizes tool outputs into a structured tactical forecast
      (supports live OpenAI-compatible LLM reasoning with automatic deterministic expert fallback).
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.toolbox = AgentToolbox(db_path)
        self.timeline_sim = MatchTimelineSimulator()

    def predict(
        self,
        team_a: str,
        team_b: str,
        best_of: int = 5,
        stage: str = "Worlds Knockout BO5",
        season: Optional[str] = None,
        season_a: Optional[str] = None,
        season_b: Optional[str] = None,
        blue_side_team: Optional[str] = None,
        use_llm: bool = True,
        as_of_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """as_of_date (YYYY-MM-DD): when set, every analytical input is restricted to
        matches played strictly before that date (walk-forward / leak-free mode)."""
        trace: List[Dict[str, Any]] = []
        eff_sa = season_a or season or "S16"
        eff_sb = season_b or season or "S16"

        # Step 1: Quant & Macro Analyst Agent
        t0 = time.perf_counter()
        quant_res = self.toolbox.tool_quant_baseline_and_pace(
            team_a=team_a,
            team_b=team_b,
            best_of=best_of,
            stage=stage,
            season=season,
            season_a=eff_sa,
            season_b=eff_sb,
            blue_side_team=blue_side_team,
            as_of_date=as_of_date,
        )
        pa = quant_res["team_a"]
        pb = quant_res["team_b"]
        trace.append(
            {
                "agent": "量化与节奏分析师 (Quant & Pace Agent)",
                "tool": "tool_quant_baseline_and_pace",
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "summary": (
                    f"提取跨赛区校准 Elo ({pa['short_name']} {pa['current_elo']} vs {pb['short_name']} {pb['current_elo']})，"
                    f"GD@15 ({pa['avg_gd15']:+.0f} vs {pb['avg_gd15']:+.0f})，控大龙率 ({pa['baron_control_rate']*100:.0f}% vs {pb['baron_control_rate']*100:.0f}%)。"
                    f"完成 BO{best_of} 马尔可夫链推演：基准胜率 {pa['short_name']} {quant_res['series_win_prob_a']*100:.1f}% vs {pb['short_name']} {quant_res['series_win_prob_b']*100:.1f}%。"
                ),
            }
        )

        # Step 2: Historical H2H & Worlds Pedigree Agent
        t1 = time.perf_counter()
        h2h_res = self.toolbox.tool_h2h_and_pedigree(pa["team_id"], pb["team_id"], as_of_date=as_of_date)
        h2h = h2h_res["h2h"]
        trace.append(
            {
                "agent": "历史交手与大赛基因分析师 (H2H & Pedigree Agent)",
                "tool": "tool_h2h_and_pedigree",
                "latency_ms": round((time.perf_counter() - t1) * 1000, 1),
                "summary": (
                    f"检索 S1–S16 历史交手共 {h2h['total_series']} 场系列赛 "
                    f"({pa['short_name']} {h2h['team_a_series_wins']}胜 - {pb['short_name']} {h2h['team_b_series_wins']}胜，"
                    f"其中世界赛/MSI 交手 {h2h['international_series']} 次)。"
                    f"大赛荣誉对比：{pa['short_name']} ({pa['worlds_titles']} S冠/{pa['msi_titles']} MSI冠) vs "
                    f"{pb['short_name']} ({pb['worlds_titles']} S冠/{pb['msi_titles']} MSI冠)。"
                ),
            }
        )

        # Step 3: Roster Matchup & Fearless Draft Tactician Agent
        t2 = time.perf_counter()
        roster_res = self.toolbox.tool_roster_and_bp_clash(
            pa["team_id"], pb["team_id"], season=season, season_a=eff_sa, season_b=eff_sb,
            as_of_date=as_of_date,
        )
        lanes = roster_res["lane_comparisons"]
        contested = roster_res["contested_picks"]
        contested_names = [f"{c['champion']} ({c['role']})" for c in contested[:5]]
        trace.append(
            {
                "agent": "五路对位与 BP 战术师 (Roster & Draft Agent)",
                "tool": "tool_roster_and_bp_clash",
                "latency_ms": round((time.perf_counter() - t2) * 1000, 1),
                "summary": (
                    f"完成五路首发对位扫描（团队战力均值 {pa['short_name']} {pa['roster_avg_rating']} vs {pb['short_name']} {pb['roster_avg_rating']}）。"
                    f"识别全局 BP 高优抢夺重叠英雄：{', '.join(contested_names) if contested_names else '双方英雄池差异化显著'}。"
                ),
            }
        )

        # Step 4: Chief Predictor Agent Synthesis & Timeline Simulation
        t3 = time.perf_counter()
        agent_Opinions = self._build_sub_agent_opinions(quant_res, h2h_res, roster_res)
        series_timelines = self.timeline_sim.generate_series_timelines(
            prof_a=pa,
            prof_b=pb,
            predicted_score=quant_res["predicted_score"],
            series_win_prob_a=quant_res["series_win_prob_a"],
        )

        llm_used = False
        report_md = ""
        if use_llm and LLM_API_KEY:
            try:
                report_md = self._call_llm_chief_predictor(quant_res, h2h_res, roster_res)
                llm_used = True
            except Exception as exc:
                report_md = self._generate_expert_tactical_report(quant_res, h2h_res, roster_res, fallback_note=str(exc))
        else:
            report_md = self._generate_expert_tactical_report(quant_res, h2h_res, roster_res)

        trace.append(
            {
                "agent": "主裁决官 Agent (Chief Predictor Arbiter)",
                "tool": f"synthesize_verdict ({'LLM: ' + LLM_MODEL if llm_used else 'Deterministic Tactical Engine'})",
                "latency_ms": round((time.perf_counter() - t3) * 1000, 1),
                "summary": (
                    f"综合三方子智能体论据并完成分钟级对局时间轴推演，裁定最终预测胜者为 {quant_res['predicted_winner']} "
                    f"(胜率 {max(quant_res['series_win_prob_a'], quant_res['series_win_prob_b'])*100:.1f}%，"
                    f"最可能比分 {quant_res['predicted_score']})。"
                ),
            }
        )

        return {
            "matchup_meta": {
                "team_a": pa["team_id"],
                "team_b": pb["team_id"],
                "best_of": best_of,
                "stage": stage,
                "season": season or "S16 (All-Time Calibrated)",
                "engine_mode": f"LLM ({LLM_MODEL})" if llm_used else "Hybrid Quant + Multi-Agent Expert Engine",
            },
            "prediction": {
                "winner_id": quant_res["predicted_winner"],
                "winner_name": pa["name"] if quant_res["predicted_winner"] == pa["team_id"] else pb["name"],
                "team_a_win_prob": quant_res["series_win_prob_a"],
                "team_b_win_prob": quant_res["series_win_prob_b"],
                "most_likely_score": quant_res["predicted_score"],
                "most_likely_score_prob": quant_res["predicted_score_prob"],
                "score_distribution": quant_res["score_distribution"],
                "silver_scrapes_prob": quant_res["silver_scrapes_prob"],
                "single_game_probs": {
                    "neutral_a": quant_res["single_game_neutral_prob_a"],
                    "a_on_blue": quant_res["single_game_blue_prob_a"],
                    "a_on_red": quant_res["single_game_red_prob_a"],
                },
            },
            "team_a_profile": pa,
            "team_b_profile": pb,
            "radar_comparison": {
                "dimensions": [
                    {"key": "laning", "label": "对线压制 (GD@15)", "max": 100},
                    {"key": "teamfight_dmg", "label": "团战输出 (DPM)", "max": 100},
                    {"key": "frontline_tank", "label": "前排承伤 (DTPM)", "max": 100},
                    {"key": "objective_ctrl", "label": "资源控制 (龙/先锋)", "max": 100},
                    {"key": "vision_macro", "label": "视野与运营推塔", "max": 100},
                    {"key": "clutch_bo5", "label": "大赛BO5韧性", "max": 100},
                ],
                "team_a_values": [
                    pa["radar_scores"]["laning"],
                    pa["radar_scores"]["teamfight_dmg"],
                    pa["radar_scores"]["frontline_tank"],
                    pa["radar_scores"]["objective_ctrl"],
                    pa["radar_scores"]["vision_macro"],
                    pa["radar_scores"]["clutch_bo5"],
                ],
                "team_b_values": [
                    pb["radar_scores"]["laning"],
                    pb["radar_scores"]["teamfight_dmg"],
                    pb["radar_scores"]["frontline_tank"],
                    pb["radar_scores"]["objective_ctrl"],
                    pb["radar_scores"]["vision_macro"],
                    pb["radar_scores"]["clutch_bo5"],
                ],
            },
            "series_timelines": series_timelines,
            "head_to_head": h2h,
            "lane_comparisons": lanes,
            "contested_picks": contested,
            "factor_attributions": quant_res["factor_attributions"],
            "sub_agent_opinions": agent_Opinions,
            "agent_execution_trace": trace,
            "tactical_report_markdown": report_md,
        }

    def _build_sub_agent_opinions(
        self, quant_res: Dict[str, Any], h2h_res: Dict[str, Any], roster_res: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        pa = quant_res["team_a"]
        pb = quant_res["team_b"]
        h2h = h2h_res["h2h"]
        lanes = roster_res["lane_comparisons"]

        # Sub-agent 1 verdict
        elo_fav = pa["short_name"] if pa["current_elo"] >= pb["current_elo"] else pb["short_name"]
        early_fav = pa["short_name"] if pa["avg_gd15"] >= pb["avg_gd15"] else pb["short_name"]
        op1 = {
            "agent_name": "量化与节奏分析师 (Quant & Pace Agent)",
            "favored_team": elo_fav,
            "confidence": f"{max(quant_res['series_win_prob_a'], quant_res['series_win_prob_b'])*100:.1f}%",
            "headline": f"{early_fav} 掌握前15分钟对线主导权，{elo_fav} 跨赛区 Elo 战力占优",
            "key_points": [
                f"跨赛区校准 Elo：{pa['short_name']} ({pa['current_elo']}) vs {pb['short_name']} ({pb['current_elo']})，历史峰值分别为 {pa['peak_elo']} ({pa['peak_season']}) 与 {pb['peak_elo']} ({pb['peak_season']})。",
                f"前15分钟经济差 (GD@15)：{pa['short_name']} 场均 {pa['avg_gd15']:+.0f} 金币（一塔率 {pa['first_tower_rate']*100:.0f}%）vs {pb['short_name']} 场均 {pb['avg_gd15']:+.0f} 金币（一塔率 {pb['first_tower_rate']*100:.0f}%）。",
                f"中后期大龙与小龙控制：{pa['short_name']} 控大龙率 {pa['baron_control_rate']*100:.0f}% / 控小龙率 {pa['dragon_control_rate']*100:.0f}%，对比 {pb['short_name']} 的 {pb['baron_control_rate']*100:.0f}% / {pb['dragon_control_rate']*100:.0f}%。",
            ],
        }

        # Sub-agent 2 verdict
        pedigree_score_a = pa["worlds_titles"] * 3 + pa["msi_titles"] * 1.5 + pa["bo5_win_rate"] * 4
        pedigree_score_b = pb["worlds_titles"] * 3 + pb["msi_titles"] * 1.5 + pb["bo5_win_rate"] * 4
        ped_fav = pa["short_name"] if pedigree_score_a >= pedigree_score_b else pb["short_name"]
        op2 = {
            "agent_name": "历史交手与大赛基因分析师 (H2H & Pedigree Agent)",
            "favored_team": ped_fav,
            "confidence": f"{50 + min(38, abs(pedigree_score_a - pedigree_score_b)*4.5):.1f}%",
            "headline": f"历史交手 {pa['short_name']} {h2h['team_a_series_wins']}:{h2h['team_b_series_wins']} {pb['short_name']}，{ped_fav} 大赛 BO5 底蕴更深厚",
            "key_points": [
                f"双方历史共交手 {h2h['total_series']} 场系列赛（小局 {h2h['team_a_game_wins']}:{h2h['team_b_game_wins']}），其中世界赛/MSI 舞台交锋 {h2h['international_series']} 次（{pa['short_name']} {h2h['intl_a_wins']}胜 : {pb['short_name']} {h2h['intl_b_wins']}胜）。",
                f"BO5 淘汰赛胜率对比：{pa['short_name']} 为 {pa['bo5_win_rate']*100:.0f}%（决胜局战歌战绩 {pa['game5_record']}），{pb['short_name']} 为 {pb['bo5_win_rate']*100:.0f}%（决胜局战绩 {pb['game5_record']}）。",
                f"战术基因画像：{pa['short_name']} 属于「{pa['style_tag']}」，而 {pb['short_name']} 属于「{pb['style_tag']}」。",
            ],
        }

        # Sub-agent 3 verdict
        roster_fav = pa["short_name"] if pa["roster_avg_rating"] >= pb["roster_avg_rating"] else pb["short_name"]
        focal_lanes = sorted(lanes, key=lambda x: abs(x["rating_diff"]), reverse=True)
        top_mismatch = focal_lanes[0] if focal_lanes else None
        op3_points = [
            f"首发五虎综合战力均值：{pa['short_name']} ({pa['roster_avg_rating']}) vs {pb['short_name']} ({pb['roster_avg_rating']})。",
        ]
        if top_mismatch:
            op3_points.append(
                f"最大对位分水岭在{top_mismatch['role_label']}：{top_mismatch['player_a']} (评分 {top_mismatch['rating_a']}, GD@15 {top_mismatch['gd15_a']:+.0f}) vs {top_mismatch['player_b']} (评分 {top_mismatch['rating_b']}, GD@15 {top_mismatch['gd15_b']:+.0f})。"
            )
        op3_points.append(
            f"红蓝方胜率差异：{pa['short_name']} 蓝方 {pa['blue_side_wr']*100:.0f}% / 红方 {pa['red_side_wr']*100:.0f}%；{pb['short_name']} 蓝方 {pb['blue_side_wr']*100:.0f}% / 红方 {pb['red_side_wr']*100:.0f}%。"
        )
        op3 = {
            "agent_name": "五路对位与 BP 战术师 (Roster & Draft Agent)",
            "favored_team": roster_fav,
            "confidence": f"{50 + min(35, abs(pa['roster_avg_rating'] - pb['roster_avg_rating'])*6.5):.1f}%",
            "headline": f"{roster_fav} 首发五虎对位均值占优，全局 BP 博弈聚焦中立资源团阵容",
            "key_points": op3_points,
        }

        return [op1, op2, op3]

    def _call_llm_chief_predictor(
        self, quant_res: Dict[str, Any], h2h_res: Dict[str, Any], roster_res: Dict[str, Any]
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        context_payload = {
            "match_stage": quant_res["stage"],
            "best_of": quant_res["best_of"],
            "quant_prediction": {
                "winner": quant_res["predicted_winner"],
                "series_win_prob_a": quant_res["series_win_prob_a"],
                "series_win_prob_b": quant_res["series_win_prob_b"],
                "most_likely_score": quant_res["predicted_score"],
                "score_distribution": quant_res["score_distribution"],
            },
            "team_a": quant_res["team_a"],
            "team_b": quant_res["team_b"],
            "head_to_head": h2h_res["h2h"],
            "lane_comparisons": roster_res["lane_comparisons"],
            "contested_picks": roster_res["contested_picks"],
        }
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_CHIEF_PREDICTOR_PROMPT},
                {
                    "role": "user",
                    "content": f"请根据以下多智能体检索数据生成深度对阵预测报告：\n```json\n{json.dumps(context_payload, ensure_ascii=False, indent=2)}\n```",
                },
            ],
            temperature=0.4,
            max_tokens=1500,
        )
        return resp.choices[0].message.content or ""

    def _generate_expert_tactical_report(
        self,
        quant_res: Dict[str, Any],
        h2h_res: Dict[str, Any],
        roster_res: Dict[str, Any],
        fallback_note: Optional[str] = None,
    ) -> str:
        pa = quant_res["team_a"]
        pb = quant_res["team_b"]
        h2h = h2h_res["h2h"]
        lanes = roster_res["lane_comparisons"]
        contested = roster_res["contested_picks"]
        bo = quant_res["best_of"]

        fav = pa if quant_res["series_win_prob_a"] >= 0.5 else pb
        dog = pb if fav["team_id"] == pa["team_id"] else pa
        fav_prob = max(quant_res["series_win_prob_a"], quant_res["series_win_prob_b"]) * 100

        # Identify focal lanes
        mid_lane = next((l for l in lanes if l["role"] == "mid"), None)
        bot_lane = next((l for l in lanes if l["role"] == "bot"), None)
        top_lane = next((l for l in lanes if l["role"] == "top"), None)

        contested_str = (
            "、".join([f"**{c['champion']}** ({c['role']})" for c in contested[:6]])
            if contested
            else "**阿兹尔**、**奎桑提**、**兰博**、**洛**"
        )

        lines = [
            f"### 1. 首席裁决官总评：{pa['name']} ({pa['region']}) vs {pb['name']} ({pb['region']})",
            f"在 **{quant_res['stage']} (BO{bo})** 的模拟推演中，多智能体预测系统综合跨赛区动态 Elo、前 15 分钟对线压制力与大赛 BO5 历史基因，裁定 **{fav['name']} ({fav['short_name']})** 以 **{fav_prob:.1f}%** 的系列赛胜率占据上风，最可能出现的大比分为 **{quant_res['predicted_score']}**（出现概率 **{quant_res['predicted_score_prob']*100:.1f}%**）。"
            + (
                f"本场对决打满五局触发『战歌局 (Silver Scrapes)』的概率高达 **{quant_res['silver_scrapes_prob']*100:.1f}%**。"
                if bo == 5
                else ""
            ),
            "",
            "### 2. 前中期对线与节奏博弈 (0–15 分钟)",
            f"- **前15分钟经济差 (GD@15) 对比**：**{pa['short_name']}** 场均 15 分钟经济差为 **{pa['avg_gd15']:+.0f}** 金币（一血率 {pa['first_blood_rate']*100:.0f}% / 一塔率 {pa['first_tower_rate']*100:.0f}%），而 **{pb['short_name']}** 场均 15 分钟经济差为 **{pb['avg_gd15']:+.0f}** 金币（一血率 {pb['first_blood_rate']*100:.0f}% / 一塔率 {pb['first_tower_rate']*100:.0f}%）。",
            f"- **节奏相性碰撞**：{pa['short_name']} 的战术标签为「{pa['style_tag']}」（场均时长 {pa['avg_duration_min']} 分钟），而 {pb['short_name']} 呈现为「{pb['style_tag']}」（场均时长 {pb['avg_duration_min']} 分钟）。"
            + (
                f" **{pa['short_name']}** 在前 15 分钟通过巢虫与先锋团滚雪球的能力更强，一旦让其在前中期拿到超过 1,200 金币的领先，其滚雪球终结率极高。"
                if pa["avg_gd15"] > pb["avg_gd15"]
                else f" **{pb['short_name']}** 在对线期与野区前期的压制力更为凶悍，会主动通过上半区碰撞撕开突破口。"
            ),
            "",
            "### 3. 中后期大龙视野运营与团战决胜 (15 分钟+)",
            f"- **史诗资源控制率**：在大龙 (Baron) 控制率上，**{pa['short_name']} ({pa['baron_control_rate']*100:.0f}%)** 对比 **{pb['short_name']} ({pb['baron_control_rate']*100:.0f}%)**；在小龙与龙魂节奏上，双方控制率分别为 **{pa['dragon_control_rate']*100:.0f}%** 与 **{pb['dragon_control_rate']*100:.0f}%**。",
            f"- **大赛与历史交手心魔 (H2H)**：双方在 S1–S16 历史库中共交锋 **{h2h['total_series']}** 场系列赛，**{pa['short_name']}** 取得 **{h2h['team_a_series_wins']} 胜 {h2h['team_b_series_wins']} 负**（小局 {h2h['team_a_game_wins']}:{h2h['team_b_game_wins']}）。"
            + (
                f" 在国际赛淘汰赛阶段，拥有 **{fav['worlds_titles']} 座全球总决赛冠军与 {fav['msi_titles']} 座 MSI 冠军** 的 {fav['short_name']} 在关键局的大龙逼团与逆风找机会能力更具统治力。"
                if (fav["worlds_titles"] + fav["msi_titles"]) > 0
                else ""
            ),
            "",
            "### 4. 五路对位焦点与全局 BP (Fearless Draft) 博弈",
        ]

        if top_lane and mid_lane and bot_lane:
            lines.extend(
                [
                    f"- **上路对抗 ({top_lane['player_a']} vs {top_lane['player_b']})**：评分 {top_lane['rating_a']} vs {top_lane['rating_b']}，场均 GD@15 为 {top_lane['gd15_a']:+.0f} vs {top_lane['gd15_b']:+.0f}。单带与团战切入时机将直接决定边线兵线权。",
                    f"- **中路皇权 ({mid_lane['player_a']} vs {mid_lane['player_b']})**：评分 {mid_lane['rating_a']} vs {mid_lane['rating_b']}，分均伤害 {mid_lane['dpm_a']:.0f} vs {mid_lane['dpm_b']:.0f}。中野线权将直接辐射第一条小龙与河道视野。",
                    f"- **下路双人组 ({bot_lane['player_a']} vs {bot_lane['player_b']})**：分均伤害高达 {bot_lane['dpm_a']:.0f} vs {bot_lane['dpm_b']:.0f}，是双方后期接管比赛的终极保险。",
                ]
            )

        lines.extend(
            [
                f"- **BP 重叠焦点池**：双方选手招牌英雄池高度重合于 {contested_str}。在 BO{bo} 系列赛中，蓝色方一抢优先级与红色方 Counter 位的交换（{pa['short_name']} 蓝方胜率 {pa['blue_side_wr']*100:.0f}% vs {pb['short_name']} 蓝方胜率 {pb['blue_side_wr']*100:.0f}%）将成为教练组博弈的核心。",
                "",
                "### 5. 双方关键获胜条件 (Key Win Conditions)",
                f"- **{fav['short_name']} 制胜公式**：",
                f"  1. 利用更稳定的前中期节奏与中立资源运营（控龙率 {fav['dragon_control_rate']*100:.0f}%），在 20 分钟前建立小龙听牌与外塔视野压制。",
                f"  2. 在系列赛后半程充分发挥英雄池深度，封锁对手核心发动机。",
                f"- **{dog['short_name']} 破局之道**：",
                f"  1. 避开对手最擅长的运营舒适区，在前 15 分钟通过野辅联动针对边路打开突破口，将比赛拖入高烈度小规模团战。",
                f"  2. 把握败者选边权带来的蓝色方强开团体系（蓝方胜率 {dog['blue_side_wr']*100:.0f}%），抢下前两局关键分打乱对手 BO{bo} 部署。",
            ]
        )

        return "\n".join(lines)
