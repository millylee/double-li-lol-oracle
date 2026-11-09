import math
import random
from typing import Any, Dict, List
from src.etl.rosters_catalog import get_champion_icon_url


class MatchTimelineSimulator:
    """
    Generates minute-by-minute (00:00 -> End) interactive match timelines,
    objective event markers, gold diff & win-probability curves, and 10-player live snapshots
    for both the AI Canonical Prediction Game and individual series games (G1..G5).
    """

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, x))))

    def generate_series_timelines(
        self,
        prof_a: Dict[str, Any],
        prof_b: Dict[str, Any],
        predicted_score: str,
        series_win_prob_a: float,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of game timeline objects:
        - Index 0: 'AI 综合推演标准局' (Expected tactical flow of the matchup)
        - Index 1..K: Individual games of the predicted series scoreline (e.g., G1..G4 for 3:1)
        """
        sa, sb = [int(x) for x in predicted_score.split(":")]
        total_games = sa + sb
        fav_a = series_win_prob_a >= 0.5

        # Construct realistic game winner sequence matching predicted_score
        series_winner = prof_a["team_id"] if sa > sb else prof_b["team_id"]
        winners = [prof_a["team_id"]] * sa + [prof_b["team_id"]] * sb
        rng = random.Random(hash(f"{prof_a['team_id']}_{prof_b['team_id']}_{predicted_score}") & 0xFFFFFFFF)
        if len(winners) > 1:
            winners.remove(series_winner)
            rng.shuffle(winners)
            winners.append(series_winner)

        timelines: List[Dict[str, Any]] = []

        # 0. AI Canonical Simulation Game
        canon_winner = prof_a["team_id"] if fav_a else prof_b["team_id"]
        timelines.append(
            self._build_single_game_timeline(
                seed_val=101,
                game_key="sim",
                label="🤖 AI 综合推演局",
                blue_prof=prof_a,
                red_prof=prof_b,
                winner_id=canon_winner,
                base_win_prob_blue=series_win_prob_a,
                archetype="canonical",
            )
        )

        # 1..K. Series Game Timelines (with loser side selection)
        blue_is_a = True
        archetypes = ["early_snowball", "baron_reversal", "dragon_soul_grind", "skirmish_bloodbath", "silver_scrapes"]
        score_running_a = 0
        score_running_b = 0

        for idx, win_id in enumerate(winners, start=1):
            blue_prof = prof_a if blue_is_a else prof_b
            red_prof = prof_b if blue_is_a else prof_a
            base_p_blue = series_win_prob_a if blue_is_a else (1.0 - series_win_prob_a)

            if win_id == prof_a["team_id"]:
                score_running_a += 1
            else:
                score_running_b += 1

            arch = archetypes[(idx - 1) % len(archetypes)]
            g_tl = self._build_single_game_timeline(
                seed_val=200 + idx * 37,
                game_key=f"g{idx}",
                label=f"Game {idx} ({score_running_a}:{score_running_b})",
                blue_prof=blue_prof,
                red_prof=red_prof,
                winner_id=win_id,
                base_win_prob_blue=base_p_blue,
                archetype=arch,
            )
            timelines.append(g_tl)

            # Loser picks Blue side for next game
            loser_id = prof_b["team_id"] if win_id == prof_a["team_id"] else prof_a["team_id"]
            blue_is_a = loser_id == prof_a["team_id"]

        return timelines

    def _build_single_game_timeline(
        self,
        seed_val: int,
        game_key: str,
        label: str,
        blue_prof: Dict[str, Any],
        red_prof: Dict[str, Any],
        winner_id: str,
        base_win_prob_blue: float,
        archetype: str,
    ) -> Dict[str, Any]:
        rng = random.Random(seed_val + (hash(blue_prof["team_id"] + red_prof["team_id"]) & 0xFFFF))
        blue_wins = winner_id == blue_prof["team_id"]

        avg_dur = int(round((blue_prof["avg_duration_min"] + red_prof["avg_duration_min"]) / 2.0))
        if archetype == "early_snowball":
            duration_min = max(25, avg_dur - 4)
            story_tag = "前期对线压制滚雪球速推"
        elif archetype == "baron_reversal":
            duration_min = min(38, avg_dur + 3)
            story_tag = "前期劣势，中期大龙团逆天翻盘"
        elif archetype == "dragon_soul_grind":
            duration_min = min(37, avg_dur + 2)
            story_tag = "小龙视野拉扯与龙魂团决胜"
        elif archetype == "silver_scrapes":
            duration_min = max(34, avg_dur + 4)
            story_tag = "生死战歌局：远古龙与双大龙巅峰决战"
        else:
            duration_min = max(28, min(35, avg_dur))
            story_tag = "AI 标准推演：前15分钟节奏过渡与大龙运营终结"

        # Expected 15m gold diff from Blue perspective
        expected_gd15 = (blue_prof["avg_gd15"] - red_prof["avg_gd15"]) * 0.75
        if archetype == "baron_reversal":
            # In a reversal game, the eventual winner is behind at 15m!
            target_gd15 = -1650.0 if blue_wins else 1650.0
        else:
            target_gd15 = (abs(expected_gd15) + 950.0) if blue_wins else -(abs(expected_gd15) + 850.0)

        final_gold_diff = rng.randint(8200, 12800) if blue_wins else -rng.randint(8200, 12800)

        # Schedule Key Objective & Teamfight Events
        events: List[Dict[str, Any]] = []
        blue_short = blue_prof["short_name"]
        red_short = red_prof["short_name"]
        blue_roster = {p["role"]: p for p in blue_prof["roster"]}
        red_roster = {p["role"]: p for p in red_prof["roster"]}

        def pick_side(bias_blue: float) -> str:
            return "blue" if rng.random() < bias_blue else "red"

        early_blue_bias = 0.68 if target_gd15 > 0 else 0.32
        late_blue_bias = 0.82 if blue_wins else 0.18

        # Event 1: First Blood (min 3-4)
        fb_min = rng.choice([3, 4])
        fb_side = pick_side(early_blue_bias)
        fb_team = blue_short if fb_side == "blue" else red_short
        fb_killer = (blue_roster if fb_side == "blue" else red_roster)["jng"]["player_name"]
        events.append({
            "minute": fb_min,
            "time_str": f"0{fb_min}:24",
            "type": "first_blood",
            "icon": "🩸",
            "side": fb_side,
            "team_short": fb_team,
            "title": f"{fb_team} 拿下一血 (First Blood)",
            "detail": f"{fb_killer} 野区联动游走击杀敌方线上英雄，斩获第一滴血 (+400g)",
            "gold_swing": 450 if fb_side == "blue" else -450,
        })

        # Event 2: First Voidgrubs & First Dragon (min 6-8)
        grub_min = 6
        grub_side = pick_side(early_blue_bias)
        grub_team = blue_short if grub_side == "blue" else red_short
        events.append({
            "minute": grub_min,
            "time_str": "06:15",
            "type": "voidgrubs",
            "icon": "👾",
            "side": grub_side,
            "team_short": grub_team,
            "title": f"{grub_team} 控制首批虚空巢虫",
            "detail": f"{grub_team} 凭借中上推线权控下 3 只虚空巢虫，推塔镀层节奏加速",
            "gold_swing": 550 if grub_side == "blue" else -550,
        })

        d1_min = 8
        d1_side = "red" if grub_side == "blue" and rng.random() < 0.6 else pick_side(early_blue_bias)
        d1_team = blue_short if d1_side == "blue" else red_short
        events.append({
            "minute": d1_min,
            "time_str": "08:10",
            "type": "dragon",
            "icon": "🐉",
            "side": d1_side,
            "team_short": d1_team,
            "title": f"{d1_team} 控下第一条小龙",
            "detail": f"{d1_team} 下路双人组抢线成功，稳稳收入首条元素亚龙",
            "gold_swing": 350 if d1_side == "blue" else -350,
        })

        # Event 3: First Tower & Rift Herald (min 14-15)
        ft_min = 14
        ft_side = "blue" if target_gd15 >= 0 else "red"
        ft_team = blue_short if ft_side == "blue" else red_short
        events.append({
            "minute": ft_min,
            "time_str": "14:08",
            "type": "first_tower",
            "icon": "🗼",
            "side": ft_side,
            "team_short": ft_team,
            "title": f"{ft_team} 推掉一血塔 & 峡谷先锋",
            "detail": f"{ft_team} 释放峡谷先锋撞掉中一塔，15分钟对线期建立显著经济视野领先",
            "gold_swing": 1100 if ft_side == "blue" else -1100,
        })

        # Event 4: Mid-game Dragon 3 / Skirmish (min 18-19)
        d3_min = 19
        d3_side = pick_side(late_blue_bias)
        d3_team = blue_short if d3_side == "blue" else red_short
        mid_carry = (blue_roster if d3_side == "blue" else red_roster)["mid"]["player_name"]
        events.append({
            "minute": d3_min,
            "time_str": "19:15",
            "type": "teamfight",
            "icon": "⚔️",
            "side": d3_side,
            "team_short": d3_team,
            "title": f"{d3_team} 河道听牌龙团战大胜",
            "detail": f"{mid_carry} 完美进场打出爆炸 AOE，{d3_team} 打出 1换3 并收下听牌小龙",
            "gold_swing": 1850 if d3_side == "blue" else -1850,
        })

        # Event 5: Baron Nashor Powerplay (min 23-25)
        baron_min = min(duration_min - 4, 24)
        baron_side = "blue" if blue_wins else "red"
        baron_team = blue_short if baron_side == "blue" else red_short
        bot_carry = (blue_roster if baron_side == "blue" else red_roster)["bot"]["player_name"]
        events.append({
            "minute": baron_min,
            "time_str": f"{baron_min}:32",
            "type": "baron",
            "icon": "👑",
            "side": baron_side,
            "team_short": baron_team,
            "title": f"{baron_team} 斩获纳什男爵 (Baron Powerplay)",
            "detail": f"{bot_carry} 团战拉满输出完成三杀，{baron_team} 拿下大龙 Buff 连拔两路外塔 (+3,600g)",
            "gold_swing": 2800 if baron_side == "blue" else -2800,
        })

        # Optional Dragon Soul / Second Baron if game >= 30m
        if duration_min >= 30:
            soul_min = min(duration_min - 2, 29)
            events.append({
                "minute": soul_min,
                "time_str": f"{soul_min}:18",
                "type": "dragon_soul",
                "icon": "🔥",
                "side": baron_side,
                "team_short": baron_team,
                "title": f"{baron_team} 解锁元素龙魂 (Dragon Soul)",
                "detail": f"{baron_team} 携大龙兵线压制下半区视野，稳稳拿下关键龙魂定下胜局",
                "gold_swing": 2100 if baron_side == "blue" else -2100,
            })

        # Final Event: Nexus Victory
        events.append({
            "minute": duration_min,
            "time_str": f"{duration_min}:00",
            "type": "nexus",
            "icon": "🏆",
            "side": baron_side,
            "team_short": baron_team,
            "title": f"{baron_team} 团灭对手推平水晶枢纽",
            "detail": f"{baron_team} 高地决胜团 0换4 摧毁敌方基地，赢下本局比赛胜利！",
            "gold_swing": 1600 if baron_side == "blue" else -1600,
        })

        event_by_min = {e["minute"]: e for e in events}

        # Build minute-by-minute frames (0 .. duration_min)
        frames: List[Dict[str, Any]] = []
        cur_diff = 0.0
        b_kills, r_kills = 0, 0
        b_towers, r_towers = 0, 0
        b_dragons, r_dragons = 0, 0
        b_barons, r_barons = 0, 0
        b_grubs, r_grubs = 0, 0

        logit_base = math.log(max(0.05, min(0.95, base_win_prob_blue)) / (1.0 - max(0.05, min(0.95, base_win_prob_blue))))

        for m in range(0, duration_min + 1):
            if m == 0:
                cur_diff = 0.0
            elif m <= 15:
                step_target = (target_gd15 / 15.0) * m
                cur_diff = 0.65 * cur_diff + 0.35 * step_target + rng.uniform(-160, 160)
            else:
                progress = (m - 15) / max(1, (duration_min - 15))
                target_now = target_gd15 + (final_gold_diff - target_gd15) * (progress ** 1.25)
                cur_diff = 0.55 * cur_diff + 0.45 * target_now + rng.uniform(-220, 220)

            if m in event_by_min:
                ev = event_by_min[m]
                cur_diff += ev["gold_swing"] * 0.45
                if ev["type"] == "first_blood":
                    if ev["side"] == "blue":
                        b_kills += 1
                    else:
                        r_kills += 1
                elif ev["type"] == "voidgrubs":
                    if ev["side"] == "blue":
                        b_grubs += 3
                        r_grubs += 1
                    else:
                        r_grubs += 3
                        b_grubs += 1
                elif ev["type"] in ("dragon", "dragon_soul"):
                    if ev["side"] == "blue":
                        b_dragons += 1
                    else:
                        r_dragons += 1
                elif ev["type"] == "first_tower":
                    if ev["side"] == "blue":
                        b_towers += 2
                    else:
                        r_towers += 2
                elif ev["type"] == "baron":
                    if ev["side"] == "blue":
                        b_barons += 1
                        b_towers = min(9, b_towers + 3)
                        b_kills += 3
                        r_kills += 1
                    else:
                        r_barons += 1
                        r_towers = min(9, r_towers + 3)
                        r_kills += 3
                        b_kills += 1
                elif ev["type"] == "teamfight":
                    if ev["side"] == "blue":
                        b_kills += 3
                        r_kills += 1
                    else:
                        r_kills += 3
                        b_kills += 1
                elif ev["type"] == "nexus":
                    if blue_wins:
                        cur_diff = max(cur_diff, abs(final_gold_diff))
                        b_towers = 11
                        b_kills += 4
                    else:
                        cur_diff = min(cur_diff, -abs(final_gold_diff))
                        r_towers = 11
                        r_kills += 4

            # Ambient kills/towers progression
            if m > 5 and m % 4 == 0 and m not in event_by_min:
                if cur_diff >= 0:
                    b_kills += 1
                    if m > 16 and b_towers < 8:
                        b_towers += 1
                else:
                    r_kills += 1
                    if m > 16 and r_towers < 8:
                        r_towers += 1

            if m > 12 and m % 6 == 0 and (b_dragons + r_dragons) < 5 and m not in event_by_min:
                if cur_diff >= 0:
                    b_dragons = min(4, b_dragons + 1)
                else:
                    r_dragons = min(4, r_dragons + 1)

            gold_diff_int = int(round(cur_diff))
            base_total_gold = 2500 + int(m * 1820 + (m ** 1.15) * 95)
            blue_gold = max(2500, int(base_total_gold + gold_diff_int / 2))
            red_gold = max(2500, int(base_total_gold - gold_diff_int / 2))

            if m == duration_min:
                win_prob_blue = 1.0 if blue_wins else 0.0
            else:
                time_weight = 0.6 + 1.4 * (m / duration_min)
                win_prob_blue = self._sigmoid(logit_base + (gold_diff_int / 2800.0) * time_weight)

            # Build 5-role player snapshots at minute m
            players_snap = []
            for r in ["top", "jng", "mid", "bot", "sup"]:
                bp = blue_roster[r]
                rp = red_roster[r]
                g_share_b = float(bp.get("gold_share", 20.0)) / 100.0
                g_share_r = float(rp.get("gold_share", 20.0)) / 100.0

                p_bgold = int(round(blue_gold * g_share_b))
                p_rgold = int(round(red_gold * g_share_r))
                p_bcs = int(round(m * float(bp.get("cs_per_min", 8.0)) * (0.3 if m < 2 else 0.92)))
                p_rcs = int(round(m * float(rp.get("cs_per_min", 8.0)) * (0.3 if m < 2 else 0.92)))

                # Cumulative damage dealt & taken scale non-linearly as teamfights ramp up
                combat_mult = 0.0 if m == 0 else (m * (0.45 + 0.65 * (m / duration_min)))
                p_bdmg = int(round(float(bp["dpm"]) * combat_mult * (1.06 if cur_diff > 0 else 0.94)))
                p_rdmg = int(round(float(rp["dpm"]) * combat_mult * (1.06 if cur_diff < 0 else 0.94)))
                p_btaken = int(round(float(bp["dtpm"]) * combat_mult))
                p_rtaken = int(round(float(rp["dtpm"]) * combat_mult))

                b_champ = (bp.get("signature_champions") or ["Azir"])[0]
                r_champ = (rp.get("signature_champions") or ["Orianna"])[0]
                players_snap.append({
                    "role": r.upper(),
                    "blue_name": bp["player_name"],
                    "red_name": rp["player_name"],
                    "blue_avatar": bp.get("avatar_url", ""),
                    "red_avatar": rp.get("avatar_url", ""),
                    "blue_champ": b_champ,
                    "red_champ": r_champ,
                    "blue_champ_icon": get_champion_icon_url(b_champ),
                    "red_champ_icon": get_champion_icon_url(r_champ),
                    "blue_gold": p_bgold,
                    "red_gold": p_rgold,
                    "gold_diff": p_bgold - p_rgold,
                    "blue_cs": p_bcs,
                    "red_cs": p_rcs,
                    "blue_dmg": p_bdmg,
                    "red_dmg": p_rdmg,
                    "blue_taken": p_btaken,
                    "red_taken": p_rtaken,
                })

            if m in event_by_min:
                event_by_min[m]["gold_diff_at_event"] = gold_diff_int

            frames.append({
                "minute": m,
                "time_label": f"{m:02d}:00",
                "blue_gold": blue_gold,
                "red_gold": red_gold,
                "gold_diff": gold_diff_int,
                "blue_win_prob": round(win_prob_blue, 4),
                "blue_kills": b_kills,
                "red_kills": r_kills,
                "blue_towers": b_towers,
                "red_towers": r_towers,
                "blue_dragons": b_dragons,
                "red_dragons": r_dragons,
                "blue_barons": b_barons,
                "red_barons": r_barons,
                "blue_grubs": b_grubs,
                "red_grubs": r_grubs,
                "players": players_snap,
            })

        return {
            "game_key": game_key,
            "label": label,
            "story_tag": story_tag,
            "duration_min": duration_min,
            "blue_team": {
                "team_id": blue_prof["team_id"],
                "name": blue_prof["name"],
                "short_name": blue_prof["short_name"],
            },
            "red_team": {
                "team_id": red_prof["team_id"],
                "name": red_prof["name"],
                "short_name": red_prof["short_name"],
            },
            "winner_id": winner_id,
            "winner_short": blue_prof["short_name"] if blue_wins else red_prof["short_name"],
            "events": events,
            "frames": frames,
        }
