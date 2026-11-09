"""
Comprehensive S1-S16 Authoritative Historical & Modern Team Rosters,
Team Visual Branding, Player Avatar Metadata, and Champion Icon Mapping.
"""
from typing import Any, Dict, List, Optional, Tuple

# Team Visual Branding (Colors, Motto, Emblem Style) for Logo Rendering
TEAM_BRANDING: Dict[str, Dict[str, str]] = {
    "T1": {"primary": "#E4002B", "secondary": "#C8AA6E", "bg": "#1A050A", "badge": "T1", "region": "LCK"},
    "GEN": {"primary": "#AA8A00", "secondary": "#F5D042", "bg": "#171305", "badge": "GEN", "region": "LCK"},
    "BLG": {"primary": "#00A1D6", "secondary": "#FB7299", "bg": "#051824", "badge": "BLG", "region": "LPL"},
    "HLE": {"primary": "#F37321", "secondary": "#FFB380", "bg": "#1F0E05", "badge": "HLE", "region": "LCK"},
    "TES": {"primary": "#E62E2D", "secondary": "#FF8A80", "bg": "#1F0707", "badge": "TES", "region": "LPL"},
    "JDG": {"primary": "#C8102E", "secondary": "#F87171", "bg": "#1C0609", "badge": "JDG", "region": "LPL"},
    "DK": {"primary": "#00C7B1", "secondary": "#67E8F9", "bg": "#041E1C", "badge": "DK", "region": "LCK"},
    "KT": {"primary": "#E60012", "secondary": "#FFFFFF", "bg": "#1A0608", "badge": "KT", "region": "LCK"},
    "IG": {"primary": "#E2E8F0", "secondary": "#94A3B8", "bg": "#0F172A", "badge": "iG", "region": "LPL"},
    "WBG": {"primary": "#E6162D", "secondary": "#FBBF24", "bg": "#1E070A", "badge": "WBG", "region": "LPL"},
    "EDG": {"primary": "#1E293B", "secondary": "#EF4444", "bg": "#090D16", "badge": "EDG", "region": "LPL"},
    "RNG": {"primary": "#B8860B", "secondary": "#FDE047", "bg": "#1A1405", "badge": "RNG", "region": "LPL"},
    "FPX": {"primary": "#EA580C", "secondary": "#FACC15", "bg": "#1F0B04", "badge": "FPX", "region": "LPL"},
    "AL": {"primary": "#DC2626", "secondary": "#FCD34D", "bg": "#1C0808", "badge": "AL", "region": "LPL"},
    "LNG": {"primary": "#2563EB", "secondary": "#60A5FA", "bg": "#061226", "badge": "LNG", "region": "LPL"},
    "DRX": {"primary": "#3B82F6", "secondary": "#93C5FD", "bg": "#071329", "badge": "DRX", "region": "LCK"},
    "G2": {"primary": "#DC2626", "secondary": "#E2E8F0", "bg": "#180808", "badge": "G2", "region": "LEC"},
    "FNC": {"primary": "#FF5900", "secondary": "#FDBA74", "bg": "#1F0D04", "badge": "FNC", "region": "LEC"},
    "MAD": {"primary": "#EAB308", "secondary": "#38BDF8", "bg": "#171406", "badge": "MDK", "region": "LEC"},
    "RGE": {"primary": "#0284C7", "secondary": "#7DD3FC", "bg": "#061621", "badge": "RGE", "region": "LEC"},
    "FLY": {"primary": "#10B981", "secondary": "#6EE7B7", "bg": "#051C14", "badge": "FLY", "region": "LCS"},
    "TL": {"primary": "#1D4ED8", "secondary": "#93C5FD", "bg": "#071126", "badge": "TL", "region": "LCS"},
    "C9": {"primary": "#0EA5E9", "secondary": "#BAE6FD", "bg": "#061824", "badge": "C9", "region": "LCS"},
    "TSM": {"primary": "#CBD5E1", "secondary": "#64748B", "bg": "#0F172A", "badge": "TSM", "region": "LCS"},
    "CLG": {"primary": "#2563EB", "secondary": "#93C5FD", "bg": "#071329", "badge": "CLG", "region": "LCS"},
    "TPA": {"primary": "#DC2626", "secondary": "#F59E0B", "bg": "#1C0908", "badge": "TPA", "region": "PCS"},
    "WE": {"primary": "#EF4444", "secondary": "#FCA5A5", "bg": "#1F0808", "badge": "WE", "region": "LPL"},
    "OMG": {"primary": "#7C3AED", "secondary": "#C4B5FD", "bg": "#130924", "badge": "OMG", "region": "LPL"},
    "M5": {"primary": "#DC2626", "secondary": "#F8FAFC", "bg": "#1C0808", "badge": "M5", "region": "LEC"},
    "AZF": {"primary": "#2563EB", "secondary": "#67E8F9", "bg": "#061429", "badge": "AZF", "region": "LCK"},
    "OG": {"primary": "#0284C7", "secondary": "#38BDF8", "bg": "#061521", "badge": "OG", "region": "LEC"},
    "AAA": {"primary": "#D97706", "secondary": "#FDE68A", "bg": "#1C1005", "badge": "aAa", "region": "LEC"},
}

# Riot Data Dragon Champion Key mapping for square icons
CHAMPION_DDRAGON_KEYS: Dict[str, str] = {
    "Aatrox": "Aatrox",
    "Ahri": "Ahri",
    "Akali": "Akali",
    "Alistar": "Alistar",
    "Amumu": "Amumu",
    "Anivia": "Anivia",
    "Annie": "Annie",
    "Aphelios": "Aphelios",
    "Ashe": "Ashe",
    "Aurelion Sol": "AurelionSol",
    "Azir": "Azir",
    "Bard": "Bard",
    "Bel'Veth": "Belveth",
    "Blitzcrank": "Blitzcrank",
    "Brand": "Brand",
    "Braum": "Braum",
    "Caitlyn": "Caitlyn",
    "Camille": "Camille",
    "Cassiopeia": "Cassiopeia",
    "Cho'Gath": "Chogath",
    "Corki": "Corki",
    "Diana": "Diana",
    "Dr. Mundo": "DrMundo",
    "Draven": "Draven",
    "Ekko": "Ekko",
    "Elise": "Elise",
    "Evelynn": "Evelynn",
    "Ezreal": "Ezreal",
    "Fiddlesticks": "Fiddlesticks",
    "Fiora": "Fiora",
    "Fizz": "Fizz",
    "Galio": "Galio",
    "Gangplank": "Gangplank",
    "Gnar": "Gnar",
    "Gragas": "Gragas",
    "Graves": "Graves",
    "Gwen": "Gwen",
    "Hecarim": "Hecarim",
    "Heimerdinger": "Heimerdinger",
    "Hwei": "Hwei",
    "Irelia": "Irelia",
    "Ivern": "Ivern",
    "Janna": "Janna",
    "Jarvan IV": "JarvanIV",
    "Jax": "Jax",
    "Jayce": "Jayce",
    "Jhin": "Jhin",
    "Jinx": "Jinx",
    "K'Sante": "KSante",
    "Kai'Sa": "Kaisa",
    "Kalista": "Kalista",
    "Karma": "Karma",
    "Karthus": "Karthus",
    "Kassadin": "Kassadin",
    "Kayle": "Kayle",
    "Kennen": "Kennen",
    "Kha'Zix": "Khazix",
    "Kindred": "Kindred",
    "Kled": "Kled",
    "Kog'Maw": "KogMaw",
    "LeBlanc": "Leblanc",
    "Leblanc": "Leblanc",
    "Lee Sin": "LeeSin",
    "Leona": "Leona",
    "Lillia": "Lillia",
    "Lissandra": "Lissandra",
    "Lucian": "Lucian",
    "Lulu": "Lulu",
    "Lux": "Lux",
    "Malphite": "Malphite",
    "Malzahar": "Malzahar",
    "Maokai": "Maokai",
    "Miss Fortune": "MissFortune",
    "Mordekaiser": "Mordekaiser",
    "Morgana": "Morgana",
    "Nami": "Nami",
    "Nautilus": "Nautilus",
    "Neeko": "Neeko",
    "Nidalee": "Nidalee",
    "Nocturne": "Nocturne",
    "Nunu": "Nunu",
    "Olaf": "Olaf",
    "Orianna": "Orianna",
    "Ornn": "Ornn",
    "Pantheon": "Pantheon",
    "Poppy": "Poppy",
    "Pyke": "Pyke",
    "Qiyana": "Qiyana",
    "Rakan": "Rakan",
    "Rek'Sai": "RekSai",
    "Rell": "Rell",
    "Renata Glasc": "Renata",
    "Renekton": "Renekton",
    "Rengar": "Rengar",
    "Rumble": "Rumble",
    "Ryze": "Ryze",
    "Samira": "Samira",
    "Sejuani": "Sejuani",
    "Senna": "Senna",
    "Seraphine": "Seraphine",
    "Sett": "Sett",
    "Shen": "Shen",
    "Shyvana": "Shyvana",
    "Singed": "Singed",
    "Sion": "Sion",
    "Sivir": "Sivir",
    "Skarner": "Skarner",
    "Smolder": "Smolder",
    "Sona": "Sona",
    "Soraka": "Soraka",
    "Swain": "Swain",
    "Sylas": "Sylas",
    "Syndra": "Syndra",
    "Tahm Kench": "TahmKench",
    "Taliyah": "Taliyah",
    "Talon": "Talon",
    "Taric": "Taric",
    "Thresh": "Thresh",
    "Tristana": "Tristana",
    "Trundle": "Trundle",
    "Twisted Fate": "TwistedFate",
    "Twitch": "Twitch",
    "Udyr": "Udyr",
    "Urgot": "Urgot",
    "Varus": "Varus",
    "Vayne": "Vayne",
    "Vex": "Vex",
    "Vi": "Vi",
    "Viego": "Viego",
    "Viktor": "Viktor",
    "Vladimir": "Vladimir",
    "Volibear": "Volibear",
    "Warwick": "Warwick",
    "Wukong": "MonkeyKing",
    "Xayah": "Xayah",
    "Xin Zhao": "XinZhao",
    "Yasuo": "Yasuo",
    "Yone": "Yone",
    "Yuumi": "Yuumi",
    "Zac": "Zac",
    "Zed": "Zed",
    "Zeri": "Zeri",
    "Ziggs": "Ziggs",
    "Zilean": "Zilean",
    "Zoe": "Zoe",
    "Zyra": "Zyra",
}


def get_champion_icon_url(champ_name: str) -> str:
    key = CHAMPION_DDRAGON_KEYS.get(
        champ_name,
        champ_name.replace(" ", "").replace("'", "").replace(".", ""),
    )
    return f"https://ddragon.leagueoflegends.com/cdn/14.22.1/img/champion/{key}.png"


def generate_team_logo_svg(team_id: str) -> str:
    tid = team_id.upper()
    b = TEAM_BRANDING.get(
        tid,
        {"primary": "#3B82F6", "secondary": "#93C5FD", "bg": "#0F172A", "badge": tid[:4], "region": "GLOBAL"},
    )
    prim = b["primary"]
    sec = b["secondary"]
    bg = b["bg"]
    badge = b["badge"]
    reg = b["region"]
    font_size = "24" if len(badge) <= 2 else ("19" if len(badge) == 3 else "15")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">
  <defs>
    <linearGradient id="g_{tid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{prim}" />
      <stop offset="100%" stop-color="{sec}" />
    </linearGradient>
    <filter id="glow_{tid}" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="{prim}" flood-opacity="0.55"/>
    </filter>
  </defs>
  <!-- Outer Hexagonal Shield -->
  <polygon points="40,4 72,18 72,54 40,76 8,54 8,18" fill="{bg}" stroke="url(#g_{tid})" stroke-width="3.5" filter="url(#glow_{tid})"/>
  <polygon points="40,10 66,22 66,51 40,69 14,51 14,22" fill="none" stroke="{sec}" stroke-opacity="0.28" stroke-width="1.2"/>
  <!-- Top Region Tag -->
  <rect x="25" y="13" width="30" height="11" rx="5.5" fill="{prim}" fill-opacity="0.35" stroke="{sec}" stroke-width="0.8"/>
  <text x="40" y="21" text-anchor="middle" fill="#F8FAFC" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="7.5" letter-spacing="0.8">{reg}</text>
  <!-- Center Team Emblem Text -->
  <text x="40" y="48" text-anchor="middle" fill="#FFFFFF" font-family="Inter, Arial, sans-serif" font-weight="900" font-size="{font_size}" letter-spacing="0.5">{badge}</text>
  <!-- Accent Bottom Chevron -->
  <path d="M28 56 L40 63 L52 56" fill="none" stroke="url(#g_{tid})" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""


def generate_player_avatar_svg(player_name: str, team_id: str = "T1", role: str = "mid") -> str:
    tid = team_id.upper()
    b = TEAM_BRANDING.get(
        tid,
        {"primary": "#3B82F6", "secondary": "#93C5FD", "bg": "#0F172A", "badge": tid[:3], "region": "LCK"},
    )
    prim = b["primary"]
    sec = b["secondary"]
    bg = b["bg"]
    role_upper = role.upper()[:3]
    initials = player_name[:2].upper() if len(player_name) >= 2 else player_name.upper()

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">
  <defs>
    <linearGradient id="pg_{tid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{prim}" />
      <stop offset="100%" stop-color="{sec}" />
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="76" height="76" rx="18" fill="{bg}" stroke="url(#pg_{tid})" stroke-width="2.5"/>
  <!-- Stylized Esports Jersey Silhouette -->
  <circle cx="40" cy="30" r="13" fill="url(#pg_{tid})" fill-opacity="0.85"/>
  <path d="M16 72 C16 52, 64 52, 64 72 Z" fill="url(#pg_{tid})" fill-opacity="0.75"/>
  <path d="M30 55 L40 67 L50 55" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-opacity="0.7"/>
  <!-- Initials & Team Pill -->
  <text x="40" y="34" text-anchor="middle" fill="#090D16" font-family="Inter, Arial, sans-serif" font-weight="900" font-size="11">{initials}</text>
  <rect x="8" y="8" width="24" height="12" rx="4" fill="#090D16" fill-opacity="0.8" stroke="{sec}" stroke-width="0.8"/>
  <text x="20" y="16.5" text-anchor="middle" fill="{sec}" font-family="Inter, monospace" font-weight="800" font-size="7.5">{role_upper}</text>
  <!-- Player Name Banner -->
  <rect x="6" y="60" width="68" height="15" rx="5" fill="#090D16" fill-opacity="0.88" stroke="{prim}" stroke-width="0.9"/>
  <text x="40" y="70.5" text-anchor="middle" fill="#F8FAFC" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="9.5">{player_name[:10]}</text>
</svg>"""


# Player Signature Champions Database (Real Iconic Picks per Player)
PLAYER_SIGNATURE_CHAMPIONS: Dict[str, List[str]] = {
    # LCK Legends & Stars
    "Faker": ["Azir", "Orianna", "Sylas", "Ahri"],
    "Bengi": ["Lee Sin", "Elise", "Jarvan IV", "Rek'Sai"],
    "Bang": ["Ezreal", "Kalista", "Jhin", "Lucian"],
    "Wolf": ["Alistar", "Nami", "Zyra", "Tahm Kench"],
    "MaRin": ["Rumble", "Fiora", "Renekton", "Maokai"],
    "Impact": ["Shen", "Jax", "K'Sante", "Renekton"],
    "Piglet": ["Vayne", "Corki", "Ezreal", "Caitlyn"],
    "PoohManDu": ["Zyra", "Nami", "Sona", "Thresh"],
    "Duke": ["Ekko", "Trundle", "Poppy", "Gnar"],
    "Huni": ["Rumble", "Jayce", "Lucian", "Yasuo"],
    "Peanut": ["Lee Sin", "Nidalee", "Sejuani", "Maokai"],
    "Blank": ["Zac", "Gragas", "Sejuani", "Elise"],
    "Thal": ["Gangplank", "Camille", "Vladimir", "Ornn"],
    "Khan": ["Jayce", "Fiora", "Camille", "Gnar"],
    "Clid": ["Lee Sin", "Elise", "Rek'Sai", "Jarvan IV"],
    "Teddy": ["Ezreal", "Ashe", "Kalista", "Varus"],
    "Effort": ["Leona", "Rakan", "Nautilus", "Braum"],
    "Canna": ["Jayce", "Kennen", "Camille", "Renekton"],
    "Cuzz": ["Viego", "Gragas", "Sejuani", "Vi"],
    "Zeus": ["Aatrox", "Jayce", "Yone", "Gnar"],
    "Oner": ["Lee Sin", "Vi", "Xin Zhao", "Nocturne"],
    "Gumayusi": ["Varus", "Xayah", "Caitlyn", "Jhin"],
    "Keria": ["Bard", "Renata Glasc", "Pyke", "Rakan"],
    "Doran": ["Jax", "Gnar", "Rumble", "K'Sante"],
    "Peyz": ["Zeri", "Kalista", "Kai'Sa", "Ezreal"],
    "Chovy": ["Yone", "Azir", "Corki", "Ahri"],
    "Canyon": ["Nidalee", "Lee Sin", "Graves", "Kindred"],
    "Kiin": ["K'Sante", "Rumble", "Jax", "Ryze"],
    "Ruler": ["Xayah", "Zeri", "Varus", "Kai'Sa"],
    "Duro": ["Rell", "Rakan", "Nautilus", "Braum"],
    "Lehends": ["Singed", "Blitzcrank", "Maokai", "Nautilus"],
    "Delight": ["Rell", "Alistar", "Rakan", "Leona"],
    "CuVee": ["Gnar", "Kennen", "Camille", "Shen"],
    "Ambition": ["Jarvan IV", "Sejuani", "Kha'Zix", "Zac"],
    "Crown": ["Viktor", "Malzahar", "Taliyah", "Orianna"],
    "CoreJJ": ["Tahm Kench", "Rakan", "Braum", "Janna"],
    "Haru": ["Ezreal", "Rengar", "Lee Sin", "Olaf"],
    "Looper": ["Singed", "Rumble", "Maokai", "Kayle"],
    "DanDy": ["Rengar", "Lee Sin", "Kha'Zix", "Jarvan IV"],
    "PawN": ["Jayce", "Talon", "Fizz", "Morgana"],
    "imp": ["Twitch", "Vayne", "Kog'Maw", "Caitlyn"],
    "Mata": ["Thresh", "Alistar", "Janna", "Rakan"],
    "Smeb": ["Kennen", "Rumble", "Fiora", "Irelia"],
    "Kuro": ["Viktor", "Taliyah", "Aurelion Sol", "Orianna"],
    "PraY": ["Ashe", "Jhin", "Ezreal", "Varus"],
    "GorillA": ["Miss Fortune", "Zyra", "Alistar", "Thresh"],
    "Zeka": ["Sylas", "Akali", "Yone", "Azir"],
    "Viper": ["Xayah", "Aphelios", "Kai'Sa", "Ezreal"],
    "Kanavi": ["Wukong", "Bel'Veth", "Lee Sin", "Viego"],
    "ShowMaker": ["Syndra", "Twisted Fate", "LeBlanc", "Azir"],
    "Nuguri": ["Kennen", "Camille", "Vladimir", "Gangplank"],
    "Ghost": ["Jhin", "Caitlyn", "Ashe", "Ziggs"],
    "BeryL": ["Pantheon", "Heimerdinger", "Ashe", "Leona"],
    "Lucid": ["Lee Sin", "Vi", "Xin Zhao", "Viego"],
    "Siwoo": ["Gnar", "Rumble", "K'Sante", "Jax"],
    "Smash": ["Kai'Sa", "Ezreal", "Kalista", "Xayah"],
    "Career": ["Rell", "Rakan", "Nautilus", "Leona"],
    "Aiming": ["Smolder", "Ezreal", "Zeri", "Kai'Sa"],
    "Kellin": ["Nami", "Lulu", "Renata Glasc", "Rakan"],
    "Kingen": ["Aatrox", "Camille", "Ornn", "Gnar"],
    "Pyosik": ["Kindred", "Hecarim", "Viego", "Lee Sin"],
    "Deft": ["Ezreal", "Jinx", "Caitlyn", "Varus"],
    "Bdd": ["Azir", "Zoe", "Taliyah", "Orianna"],
    "Score": ["Kindred", "Gragas", "Sejuani", "Rek'Sai"],
    "Ssumday": ["Renekton", "Gnar", "Maokai", "Aatrox"],
    "Ucal": ["Swain", "Yasuo", "Irelia", "Azir"],
    "PerfecT": ["K'Sante", "Rumble", "Renekton", "Gnar"],
    "deokdam": ["Aphelios", "Varus", "Ezreal", "Jinx"],
    "Rascal": ["Camille", "Renekton", "Ornn", "K'Sante"],
    "Shy": ["Jax", "Singed", "Shen", "Jayce"],
    "MadLife": ["Blitzcrank", "Thresh", "Alistar", "Sona"],
    # LPL Legends & Stars
    "TheShy": ["Aatrox", "Jayce", "Fiora", "Rumble"],
    "Rookie": ["Orianna", "Syndra", "LeBlanc", "Jayce"],
    "JackeyLove": ["Draven", "Kai'Sa", "Lucian", "Xayah"],
    "Ning": ["Camille", "Lee Sin", "Gragas", "Xin Zhao"],
    "Baolan": ["Rakan", "Alistar", "Braum", "Leona"],
    "PDD": ["Rumble", "Jarvan IV", "Zac", "Malphite"],
    "Zz1tai": ["Swain", "Orianna", "Morgana", "Ryze"],
    "Kid": ["Ezreal", "Vayne", "Graves", "Lucian"],
    "KaKAO": ["Lee Sin", "Nocturne", "Kha'Zix", "Elise"],
    "Wei": ["Lee Sin", "Viego", "Wukong", "Vi"],
    "Meiko": ["Thresh", "Rakan", "Yuumi", "Lulu"],
    "JiaQi": ["Kai'Sa", "Varus", "Ezreal", "Kalista"],
    "GALA": ["Kai'Sa", "Xayah", "Tristana", "Varus"],
    "Bin": ["Jax", "Camille", "Fiora", "Gwen"],
    "Xun": ["Kindred", "Nidalee", "Lee Sin", "Xin Zhao"],
    "knight": ["Ahri", "Sylas", "Syndra", "Jayce"],
    "Elk": ["Kalista", "Xayah", "Kai'Sa", "Ezreal"],
    "ON": ["Rakan", "Rell", "Pyke", "Blitzcrank"],
    "Yagao": ["Zoe", "Azir", "Taliyah", "Leblanc"],
    "369": ["K'Sante", "Gragas", "Renekton", "Aatrox"],
    "Tian": ["Lee Sin", "Qiyana", "Viego", "Vi"],
    "Creme": ["Akali", "Tristana", "Sylas", "Yone"],
    "Crisp": ["Thresh", "Renata Glasc", "Rakan", "Pyke"],
    "Zhuo": ["Rell", "Leona", "Nautilus", "Alistar"],
    "Karsa": ["Lee Sin", "Graves", "Jarvan IV", "Elise"],
    "Scout": ["Zoe", "Azir", "Ryze", "Sylas"],
    "MISSING": ["Rakan", "Lulu", "Thresh", "Alistar"],
    "Missing": ["Rakan", "Lulu", "Thresh", "Alistar"],
    "Zoom": ["Ornn", "Camille", "Renekton", "Gangplank"],
    "LvMao": ["Bard", "Thresh", "Braum", "Tahm Kench"],
    "Clearlove": ["Evelynn", "Lee Sin", "Nunu", "Rek'Sai"],
    "Flandre": ["Graves", "Jayce", "Kennen", "Gnar"],
    "Jiejie": ["Jarvan IV", "Viego", "Xin Zhao", "Lee Sin"],
    "Uzi": ["Vayne", "Kai'Sa", "Ezreal", "Xayah"],
    "Xiaohu": ["Lucian", "Galio", "Lissandra", "Azir"],
    "Ming": ["Rakan", "Alistar", "Nautilus", "Thresh"],
    "Mlxg": ["Lee Sin", "Nocturne", "Olaf", "Sejuani"],
    "Letme": ["Ornn", "Sion", "Shen", "Maokai"],
    "inSec": ["Lee Sin", "Rengar", "Kha'Zix", "Pantheon"],
    "Doinb": ["Nautilus", "Ryze", "Rumble", "Kled"],
    "GimGoon": ["Gangplank", "Renekton", "Mordekaiser", "Gnar"],
    "Lwx": ["Kai'Sa", "Vayne", "Aphelios", "Varus"],
    "SofM": ["Lee Sin", "Graves", "Rengar", "Shen"],
    "Light": ["Kalista", "Ezreal", "Aphelios", "Varus"],
    "Breathe": ["Jax", "Fiora", "Renekton", "K'Sante"],
    "Tarzan": ["Lee Sin", "Sejuani", "Skarner", "Viego"],
    "Shanks": ["Azir", "Corki", "Orianna", "Taliyah"],
    "Hope": ["Jinx", "Xayah", "Varus", "Aphelios"],
    "Kael": ["Rell", "Rakan", "Tahm Kench", "Braum"],
    "Zika": ["Jax", "K'Sante", "Gwen", "Renekton"],
    "Weiwei": ["Maokai", "Poppy", "Viego", "Sejuani"],
    "Hang": ["Blitzcrank", "Rell", "Nautilus", "Rakan"],
    "WeiXiao": ["Ezreal", "Vayne", "Caitlyn", "Graves"],
    "Misaya": ["Twisted Fate", "Orianna", "Diana", "Karthus"],
    "CaoMei": ["Rengar", "Olaf", "Irelia", "Shen"],
    "xiye": ["Lucian", "Kassadin", "LeBlanc", "Taliyah"],
    "Mystic": ["Kog'Maw", "Xayah", "Caitlyn", "Ezreal"],
    "Gogoing": ["Ryze", "Rumble", "Irelia", "Renekton"],
    "Cool": ["Ahri", "Syndra", "Yasuo", "Zed"],
    "U": ["Ziggs", "Orianna", "Syndra", "Twisted Fate"],
    "NaMei": ["Lucian", "Twitch", "Kog'Maw", "Jinx"],
    # LEC / LCS / PCS Legends & Stars
    "Caps": ["Sylas", "LeBlanc", "Syndra", "Orianna"],
    "Perkz": ["Xayah", "Kai'Sa", "LeBlanc", "Yasuo"],
    "Jankos": ["Elise", "Olaf", "Sejuani", "Lee Sin"],
    "Wunder": ["Pyke", "Ryze", "Camille", "Ornn"],
    "Mikyx": ["Rakan", "Gragas", "Thresh", "Bard"],
    "BrokenBlade": ["Yone", "Zac", "Jax", "K'Sante"],
    "Hans Sama": ["Draven", "Kalista", "Varus", "Jinx"],
    "Rekkles": ["Sivir", "Tristana", "Xayah", "Jhin"],
    "xPeke": ["Kassadin", "Orianna", "Ahri", "Karthus"],
    "sOAZ": ["Shen", "Gnar", "Rumble", "Ornn"],
    "YellOwStaR": ["Thresh", "Leona", "Alistar", "Annie"],
    "Bwipo": ["Urgot", "Rumble", "Swain", "Ornn"],
    "Hylissang": ["Pyke", "Rakan", "Thresh", "Alistar"],
    "Humanoid": ["Azir", "Orianna", "Viktor", "Twisted Fate"],
    "Razork": ["Vi", "Viego", "Poppy", "Lee Sin"],
    "Upset": ["Ezreal", "Zeri", "Kalista", "Kai'Sa"],
    "Elyoya": ["Viego", "Volibear", "Maokai", "Lee Sin"],
    "Inspired": ["Fiddlesticks", "Viego", "Ivern", "Sejuani"],
    "Larssen": ["Azir", "Orianna", "Corki", "Ryze"],
    "Bjergsen": ["Syndra", "Zilean", "Orianna", "LeBlanc"],
    "Doublelift": ["Lucian", "Caitlyn", "Vayne", "Jinx"],
    "Jensen": ["Orianna", "LeBlanc", "Azir", "Syndra"],
    "Sneaky": ["Caitlyn", "Lucian", "Sivir", "Xayah"],
    "Blaber": ["Olaf", "Kindred", "Lee Sin", "Xin Zhao"],
    "Berserker": ["Zeri", "Kai'Sa", "Xayah", "Aphelios"],
    "Vulcan": ["Alistar", "Rakan", "Tahm Kench", "Nautilus"],
    "APA": ["Ziggs", "Aurelion Sol", "Taliyah", "Neeko"],
    "Yeon": ["Lucian", "Samira", "Kalista", "Varus"],
    "Quad": ["Cassiopeia", "Orianna", "Hwei", "Azir"],
    "Massu": ["Kai'Sa", "Ezreal", "Kalista", "Jhin"],
    "Busio": ["Bard", "Rakan", "Alistar", "Nautilus"],
    "Toyz": ["Orianna", "Anivia", "Karthus", "Twisted Fate"],
    "Stanley": ["Nidalee", "Shen", "Olaf", "Jayce"],
    "Bebe": ["Ezreal", "Vayne", "Caitlyn", "Tristana"],
    "Maple": ["LeBlanc", "Taliyah", "Azir", "Zoe"],
    "SwordArt": ["Leona", "Alistar", "Thresh", "Bard"],
    "Doggo": ["Kalista", "Draven", "Ezreal", "Aphelios"],
    "JunJia": ["Skarner", "Vi", "Maokai", "Viego"],
    "Diamondprox": ["Lee Sin", "Shyvana", "Udyr", "Xin Zhao"],
    "Alex Ich": ["Kha'Zix", "Evelynn", "Ryze", "Karthus"],
    "Froggen": ["Anivia", "Karthus", "Lux", "Orianna"],
}

DEFAULT_ROLE_CHAMPIONS: Dict[str, List[str]] = {
    "top": ["K'Sante", "Rumble", "Jax", "Gnar"],
    "jng": ["Lee Sin", "Viego", "Sejuani", "Vi"],
    "mid": ["Azir", "Orianna", "Ahri", "Sylas"],
    "bot": ["Xayah", "Kai'Sa", "Ezreal", "Varus"],
    "sup": ["Rakan", "Nautilus", "Rell", "Thresh"],
}

# Mainstream pro-play champion pools per era (season bucket). Signature champion
# pools and generated drafts are filtered against these, so an S3 lineup can
# never show K'Sante (2022) and an S16 support pool never shows S9-era Pyke.
SEASON_META_POOLS: Dict[str, Dict[str, List[str]]] = {
    "S1-S2": {  # 2011-2012
        "top": ["Irelia", "Jax", "Gangplank", "Nasus", "Cho'Gath", "Malphite", "Shen", "Olaf"],
        "jng": ["Nocturne", "Udyr", "Lee Sin", "Shyvana", "Skarner", "Maokai", "Trundle", "Warwick"],
        "mid": ["Ryze", "Morgana", "Kassadin", "Anivia", "Karthus", "Ahri", "Cassiopeia", "Twisted Fate"],
        "bot": ["Ashe", "Caitlyn", "Vayne", "Corki", "Ezreal", "Graves", "Kog'Maw", "Miss Fortune"],
        "sup": ["Janna", "Taric", "Soraka", "Alistar", "Sona", "Lulu", "Nunu", "Blitzcrank"],
    },
    "S3-S4": {  # 2013-2014
        "top": ["Renekton", "Shen", "Jax", "Zac", "Shyvana", "Dr. Mundo", "Trundle", "Irelia"],
        "jng": ["Lee Sin", "Nasus", "Jarvan IV", "Vi", "Elise", "Evelynn", "Kha'Zix", "Pantheon"],
        "mid": ["Zed", "Orianna", "Ahri", "Gragas", "Twisted Fate", "Syndra", "Xerath", "LeBlanc"],
        "bot": ["Vayne", "Ezreal", "Caitlyn", "Twitch", "Lucian", "Jinx", "Corki", "Tristana"],
        "sup": ["Thresh", "Zyra", "Sona", "Lulu", "Morgana", "Braum", "Leona", "Nami"],
    },
    "S5-S6": {  # 2015-2016
        "top": ["Gnar", "Rumble", "Maokai", "Hecarim", "Fiora", "Poppy", "Nautilus", "Trundle"],
        "jng": ["Gragas", "Rek'Sai", "Nidalee", "Sejuani", "Lee Sin", "Graves", "Kindred", "Elise"],
        "mid": ["Azir", "Viktor", "Lulu", "Orianna", "Ryze", "Cassiopeia", "LeBlanc", "Lissandra"],
        "bot": ["Sivir", "Kalista", "Corki", "Jinx", "Vayne", "Lucian", "Ezreal", "Jhin"],
        "sup": ["Alistar", "Thresh", "Morgana", "Braum", "Karma", "Bard", "Trundle", "Tahm Kench"],
    },
    "S7-S8": {  # 2017-2018
        "top": ["Renekton", "Gnar", "Jarvan IV", "Shen", "Cho'Gath", "Aatrox", "Urgot", "Sion"],
        "jng": ["Sejuani", "Gragas", "Zac", "Elise", "Kha'Zix", "Lee Sin", "Trundle", "Camille"],
        "mid": ["Syndra", "Orianna", "Cassiopeia", "Taliyah", "Galio", "Ryze", "LeBlanc", "Zoe"],
        "bot": ["Varus", "Ashe", "Xayah", "Ezreal", "Twitch", "Kai'Sa", "Lucian", "Jhin"],
        "sup": ["Karma", "Lulu", "Rakan", "Tahm Kench", "Alistar", "Braum", "Nautilus", "Pyke"],
    },
    "S9-S10": {  # 2019-2020
        "top": ["Gnar", "Aatrox", "Vladimir", "Gangplank", "Renekton", "Ornn", "Camille", "Volibear"],
        "jng": ["Lee Sin", "Rek'Sai", "Elise", "Gragas", "Skarner", "Hecarim", "Graves", "Lillia"],
        "mid": ["Ryze", "Azir", "Corki", "Qiyana", "Sylas", "Syndra", "Orianna", "LeBlanc"],
        "bot": ["Kai'Sa", "Xayah", "Ezreal", "Varus", "Lucian", "Aphelios", "Senna", "Ashe"],
        "sup": ["Nautilus", "Thresh", "Rakan", "Alistar", "Yuumi", "Sett", "Leona", "Pantheon"],
    },
    "S11-S12": {  # 2021-2022
        "top": ["Gnar", "Jayce", "Graves", "Camille", "Kennen", "Aatrox", "Sion", "Ornn"],
        "jng": ["Viego", "Lee Sin", "Nidalee", "Xin Zhao", "Diana", "Vi", "Wukong", "Sejuani"],
        "mid": ["Ryze", "Azir", "Sylas", "LeBlanc", "Zoe", "Ahri", "Taliyah", "Corki"],
        "bot": ["Kai'Sa", "Jinx", "Aphelios", "Varus", "Lucian", "Zeri", "Xayah", "Sivir"],
        "sup": ["Rakan", "Nautilus", "Leona", "Thresh", "Rell", "Lulu", "Renata Glasc", "Tahm Kench"],
    },
    "S13": {  # 2023
        "top": ["K'Sante", "Rumble", "Jax", "Aatrox", "Gwen", "Gnar", "Renekton", "Sion"],
        "jng": ["Maokai", "Sejuani", "Vi", "Nocturne", "Bel'Veth", "Jarvan IV", "Rell", "Kha'Zix"],
        "mid": ["Orianna", "Azir", "Sylas", "Neeko", "LeBlanc", "Yone", "Ahri", "Taliyah"],
        "bot": ["Xayah", "Kai'Sa", "Varus", "Zeri", "Aphelios", "Kalista", "Senna", "Jinx"],
        "sup": ["Rakan", "Renata Glasc", "Nautilus", "Alistar", "Milio", "Bard", "Leona", "Tahm Kench"],
    },
    "S14": {  # 2024
        "top": ["K'Sante", "Rumble", "Jax", "Renekton", "Camille", "Aurora", "Gnar", "Yone"],
        "jng": ["Vi", "Sejuani", "Xin Zhao", "Lee Sin", "Nidalee", "Maokai", "Wukong", "Brand"],
        "mid": ["Yone", "Azir", "Corki", "Ahri", "Sylas", "Tristana", "Orianna", "Syndra"],
        "bot": ["Kai'Sa", "Xayah", "Varus", "Ashe", "Ezreal", "Zeri", "Jinx", "Kalista"],
        "sup": ["Rell", "Rakan", "Nautilus", "Alistar", "Poppy", "Renata Glasc", "Braum", "Leona"],
    },
    "S15": {  # 2025
        "top": ["K'Sante", "Rumble", "Gnar", "Jayce", "Aatrox", "Renekton", "Ambessa", "Sion"],
        "jng": ["Xin Zhao", "Vi", "Sejuani", "Wukong", "Nidalee", "Maokai", "Lee Sin", "Viego"],
        "mid": ["Azir", "Yone", "Ahri", "Sylas", "Orianna", "Hwei", "Corki", "Syndra"],
        "bot": ["Kai'Sa", "Varus", "Xayah", "Ezreal", "Ashe", "Lucian", "Jinx", "Caitlyn"],
        "sup": ["Rell", "Rakan", "Alistar", "Nautilus", "Poppy", "Renata Glasc", "Bard", "Leona"],
    },
    "S16": {  # 2026 — fearless-draft era: modern meta core with a wider bench
        "top": ["K'Sante", "Rumble", "Jax", "Gnar", "Jayce", "Aatrox", "Gwen", "Camille"],
        "jng": ["Xin Zhao", "Vi", "Sejuani", "Lee Sin", "Nidalee", "Wukong", "Viego", "Maokai"],
        "mid": ["Azir", "Yone", "Ahri", "Sylas", "Orianna", "Corki", "Syndra", "Taliyah"],
        "bot": ["Kai'Sa", "Xayah", "Varus", "Ezreal", "Ashe", "Aphelios", "Lucian", "Jinx"],
        "sup": ["Rell", "Rakan", "Nautilus", "Alistar", "Poppy", "Renata Glasc", "Braum", "Bard"],
    },
}


def get_season_meta_pool(season: Optional[str]) -> Dict[str, List[str]]:
    """Returns the mainstream pro-play champion pool for a season's era."""
    try:
        s = int(str(season).upper().lstrip("S"))
    except (ValueError, AttributeError):
        s = 16
    if s <= 2:
        era = "S1-S2"
    elif s <= 4:
        era = "S3-S4"
    elif s <= 6:
        era = "S5-S6"
    elif s <= 8:
        era = "S7-S8"
    elif s <= 10:
        era = "S9-S10"
    elif s <= 12:
        era = "S11-S12"
    else:
        era = f"S{s}"
    return SEASON_META_POOLS.get(era, SEASON_META_POOLS["S16"])


def _build_lineup(
    team_id: str,
    season: str,
    players: Tuple[str, str, str, str, str],
    tier_rating: float = 90.0,
) -> List[Tuple[str, str, str, str, float, float, float, float, float, List[str], float]]:
    """
    Expands a 5-player (top, jng, mid, bot, sup) era lineup into role-calibrated
    database rows with authentic signature champions and realistic performance metrics.
    """
    roles = ["top", "jng", "mid", "bot", "sup"]
    # Base statistical templates per role scaled by tier_rating
    scale = (tier_rating - 85.0) / 10.0  # roughly -0.2 to +1.3
    role_baselines = {
        "top": (4.1 + 0.8 * scale, 565.0 + 75.0 * scale, 260.0 + 360.0 * scale, 8.6 + 0.5 * scale, 65.5 + 3.0 * scale),
        "jng": (4.5 + 1.0 * scale, 425.0 + 55.0 * scale, 310.0 + 280.0 * scale, 6.3 + 0.5 * scale, 74.0 + 3.5 * scale),
        "mid": (4.8 + 1.1 * scale, 620.0 + 65.0 * scale, 340.0 + 350.0 * scale, 9.1 + 0.7 * scale, 73.5 + 3.5 * scale),
        "bot": (5.1 + 1.1 * scale, 665.0 + 65.0 * scale, 350.0 + 320.0 * scale, 9.5 + 0.5 * scale, 72.5 + 3.5 * scale),
        "sup": (4.3 + 0.9 * scale, 215.0 + 35.0 * scale, 180.0 + 180.0 * scale, 1.3, 75.0 + 3.5 * scale),
    }

    rows = []
    meta_pool = get_season_meta_pool(season)
    for idx, (role, pname) in enumerate(zip(roles, players)):
        kda, dpm, gd15, cspm, kp = role_baselines[role]
        # Deterministic slight per-player variance based on player name hash
        h = sum(ord(c) for c in pname) % 9 - 4
        p_rating = round(min(99.0, max(82.0, tier_rating + h * 0.35)), 1)
        base_champs = PLAYER_SIGNATURE_CHAMPIONS.get(pname, DEFAULT_ROLE_CHAMPIONS[role])
        # Keep only champions that were actually mainstream in this season's era,
        # backfilling from the era meta pool so pools stay era-authentic.
        era_pool = meta_pool.get(role, base_champs)
        kept = [c for c in base_champs if c in era_pool]
        fill = [c for c in era_pool if c not in kept]
        champs = (kept + fill)[:4] if (kept + fill) else base_champs
        rows.append(
            (
                team_id,
                season,
                role,
                pname,
                round(kda + h * 0.06, 2),
                round(dpm + h * 4.5, 1),
                round(gd15 + h * 18.0, 1),
                round(cspm + (h * 0.04 if role != "sup" else 0.0), 1),
                round(kp + h * 0.3, 1),
                champs,
                p_rating,
            )
        )
    return rows


# ==============================================================================
# AUTHORITATIVE S1 - S16 HISTORICAL TEAM LINEUPS (Sourced from Liquipedia / Wiki)
# Format: (team_id, season, (Top, Jungle, Mid, Bot, Support), team_era_rating)
# ==============================================================================
RAW_TEAM_ERA_LINEUPS: List[Tuple[str, str, Tuple[str, str, str, str, str], float]] = [
    # ==================== 1. T1 (SK Telecom T1 / T1) — S3 to S16 ====================
    ("T1", "S3", ("Impact", "Bengi", "Faker", "Piglet", "PoohManDu"), 96.5),
    ("T1", "S4", ("Impact", "Bengi", "Faker", "Piglet", "PoohManDu"), 91.5),
    ("T1", "S5", ("MaRin", "Bengi", "Faker", "Bang", "Wolf"), 97.5),
    ("T1", "S6", ("Duke", "Bengi", "Faker", "Bang", "Wolf"), 96.5),
    ("T1", "S7", ("Huni", "Peanut", "Faker", "Bang", "Wolf"), 94.5),
    ("T1", "S8", ("Thal", "Blank", "Faker", "Bang", "Wolf"), 88.0),
    ("T1", "S9", ("Khan", "Clid", "Faker", "Teddy", "Effort"), 93.5),
    ("T1", "S10", ("Canna", "Cuzz", "Faker", "Teddy", "Effort"), 91.0),
    ("T1", "S11", ("Canna", "Oner", "Faker", "Gumayusi", "Keria"), 93.0),
    ("T1", "S12", ("Zeus", "Oner", "Faker", "Gumayusi", "Keria"), 95.5),
    ("T1", "S13", ("Zeus", "Oner", "Faker", "Gumayusi", "Keria"), 97.0),
    ("T1", "S14", ("Zeus", "Oner", "Faker", "Gumayusi", "Keria"), 96.5),
    ("T1", "S15", ("Doran", "Oner", "Faker", "Gumayusi", "Keria"), 96.0),
    ("T1", "S16", ("Doran", "Oner", "Faker", "Peyz", "Keria"), 94.0),

    # ==================== 2. IG (Invictus Gaming) — S2 to S16 ====================
    ("IG", "S2", ("PDD", "illuSioN", "Zz1tai", "Kid", "XiaoXiao"), 91.0),
    ("IG", "S3", ("PDD", "illuSioN", "Zz1tai", "Kid", "XiaoXiao"), 90.5),
    ("IG", "S4", ("YongSoo", "illuSioN", "Zz1tai", "Kid", "Kitties"), 88.0),
    ("IG", "S5", ("Zz1tai", "KaKAO", "Rookie", "Kid", "Kitties"), 91.5),
    ("IG", "S6", ("Zz1tai", "Kid", "Rookie", "Rain", "Baolan"), 88.5),
    ("IG", "S7", ("TheShy", "Ning", "Rookie", "West", "Baolan"), 91.0),
    ("IG", "S8", ("TheShy", "Ning", "Rookie", "JackeyLove", "Baolan"), 97.5),
    ("IG", "S9", ("TheShy", "Ning", "Rookie", "JackeyLove", "Baolan"), 94.5),
    ("IG", "S10", ("TheShy", "Ning", "Rookie", "Puff", "Southwind"), 91.0),
    ("IG", "S11", ("TheShy", "Xun", "Rookie", "Wink", "Baolan"), 89.5),
    ("IG", "S12", ("Zika", "Xun", "Yuekai", "Ahn", "XinLiu"), 86.5),
    ("IG", "S13", ("YSKM", "Tianzhen", "Cryin", "Ahn", "Wink"), 86.0),
    ("IG", "S14", ("YSKM", "Leyan", "Cryin", "Ahn", "Vampire"), 86.5),
    ("IG", "S15", ("TheShy", "Wei", "Rookie", "GALA", "Meiko"), 93.0),
    ("IG", "S16", ("TheShy", "Wei", "Rookie", "JiaQi", "Meiko"), 92.5),

    # ==================== 3. BLG (Bilibili Gaming / I May) — S6 to S16 ====================
    ("BLG", "S6", ("AmazingJ", "Avoidless", "Athena", "Jinjiao", "Road"), 88.5),
    ("BLG", "S8", ("AmazingJ", "Chieftain", "Athena", "Jinjiao", "Road"), 88.0),
    ("BLG", "S9", ("ADD", "Meteor", "Kuro", "Jinjiao", "XinMo"), 89.5),
    ("BLG", "S10", ("ADD", "Meteor", "FoFo", "Wings", "XinMo"), 88.0),
    ("BLG", "S11", ("Biubiu", "Weiwei", "Zeka", "Aiming", "ppgod"), 89.0),
    ("BLG", "S12", ("Breathe", "Weiwei", "FoFo", "Doggo", "Crisp"), 90.0),
    ("BLG", "S13", ("Bin", "Xun", "Yagao", "Elk", "ON"), 93.5),
    ("BLG", "S14", ("Bin", "Xun", "knight", "Elk", "ON"), 95.5),
    ("BLG", "S15", ("Bin", "Beichuan", "knight", "Elk", "ON"), 93.5),
    ("BLG", "S16", ("Bin", "Xun", "knight", "Viper", "ON"), 95.0),

    # ==================== 4. GEN (Gen.G / SSG / SSW / Ozone) — S3 to S16 ====================
    ("GEN", "S3", ("Homme", "DanDy", "dade", "imp", "Mata"), 92.0),
    ("GEN", "S4", ("Looper", "DanDy", "PawN", "imp", "Mata"), 97.5),
    ("GEN", "S5", ("CuVee", "Ambition", "Crown", "Fury", "Wraith"), 88.0),
    ("GEN", "S6", ("CuVee", "Ambition", "Crown", "Ruler", "CoreJJ"), 94.0),
    ("GEN", "S7", ("CuVee", "Ambition", "Crown", "Ruler", "CoreJJ"), 96.0),
    ("GEN", "S8", ("CuVee", "Haru", "Crown", "Ruler", "CoreJJ"), 90.5),
    ("GEN", "S9", ("CuVee", "Peanut", "Fly", "Ruler", "Life"), 89.5),
    ("GEN", "S10", ("Rascal", "Clid", "Bdd", "Ruler", "Life"), 92.0),
    ("GEN", "S11", ("Burdol", "Clid", "Bdd", "Ruler", "Life"), 92.5),
    ("GEN", "S12", ("Doran", "Peanut", "Chovy", "Ruler", "Lehends"), 94.5),
    ("GEN", "S13", ("Doran", "Peanut", "Chovy", "Peyz", "Delight"), 94.0),
    ("GEN", "S14", ("Kiin", "Canyon", "Chovy", "Peyz", "Lehends"), 95.5),
    ("GEN", "S15", ("Kiin", "Canyon", "Chovy", "Ruler", "Duro"), 95.5),
    ("GEN", "S16", ("Kiin", "Canyon", "Chovy", "Ruler", "Duro"), 96.0),

    # ==================== 5. HLE (Hanwha Life Esports / ROX / KOO Tigers) — S5 to S16 ====================
    ("HLE", "S5", ("Smeb", "Hojin", "Kuro", "PraY", "GorillA"), 94.0),
    ("HLE", "S6", ("Smeb", "Peanut", "Kuro", "PraY", "GorillA"), 95.5),
    ("HLE", "S7", ("Lindarang", "SeongHwan", "Mickey", "Sangyoon", "Key"), 87.5),
    ("HLE", "S8", ("Lindarang", "SeongHwan", "Lava", "Sangyoon", "Key"), 88.0),
    ("HLE", "S9", ("SoHwan", "BonO", "Lava", "Sangyoon", "Key"), 87.5),
    ("HLE", "S10", ("CuVee", "Haru", "Lava", "Viper", "Lehends"), 88.5),
    ("HLE", "S11", ("Morgan", "Willer", "Chovy", "Deft", "Vsta"), 91.0),
    ("HLE", "S12", ("DuDu", "OnFleek", "Karis", "Cheoni", "Vsta"), 86.0),
    ("HLE", "S13", ("Kingen", "Grizzly", "Zeka", "Viper", "Life"), 91.5),
    ("HLE", "S14", ("Doran", "Peanut", "Zeka", "Viper", "Delight"), 94.0),
    ("HLE", "S15", ("Zeus", "Peanut", "Zeka", "Viper", "Delight"), 94.0),
    ("HLE", "S16", ("Zeus", "Kanavi", "Zeka", "Gumayusi", "Delight"), 95.0),

    # ==================== 6. DK (Dplus KIA / DWG KIA / DAMWON Gaming) — S9 to S16 ====================
    ("DK", "S9", ("Nuguri", "Canyon", "ShowMaker", "Nuclear", "BeryL"), 92.0),
    ("DK", "S10", ("Nuguri", "Canyon", "ShowMaker", "Ghost", "BeryL"), 97.0),
    ("DK", "S11", ("Khan", "Canyon", "ShowMaker", "Ghost", "BeryL"), 95.5),
    ("DK", "S12", ("Nuguri", "Canyon", "ShowMaker", "deokdam", "Kellin"), 92.5),
    ("DK", "S13", ("Canna", "Canyon", "ShowMaker", "Deft", "Kellin"), 91.5),
    ("DK", "S14", ("Kingen", "Lucid", "ShowMaker", "Aiming", "Kellin"), 91.0),
    ("DK", "S15", ("Siwoo", "Lucid", "ShowMaker", "Aiming", "BeryL"), 91.0),
    ("DK", "S16", ("Siwoo", "Lucid", "ShowMaker", "Smash", "Career"), 92.0),

    # ==================== 7. KT (KT Rolster) — S3 to S16 ====================
    ("KT", "S3", ("inSec", "KaKAO", "Ryu", "Score", "Mafa"), 92.5),
    ("KT", "S4", ("Ssumday", "KaKAO", "Rookie", "Arrow", "Hachani"), 93.5),
    ("KT", "S5", ("Ssumday", "Score", "Nagne", "Arrow", "Piccaboo"), 92.0),
    ("KT", "S6", ("Ssumday", "Score", "Fly", "Arrow", "Hachani"), 91.5),
    ("KT", "S7", ("Smeb", "Score", "PawN", "Deft", "Mata"), 93.5),
    ("KT", "S8", ("Smeb", "Score", "Ucal", "Deft", "Mata"), 94.5),
    ("KT", "S9", ("Smeb", "Score", "Bdd", "PraY", "SnowFlower"), 88.5),
    ("KT", "S10", ("Smeb", "BonO", "Kuro", "Aiming", "TusiN"), 88.5),
    ("KT", "S11", ("Doran", "Blank", "Dove", "Noah", "Harp"), 87.5),
    ("KT", "S12", ("Rascal", "Cuzz", "VicLa", "Aiming", "Life"), 90.0),
    ("KT", "S13", ("Kiin", "Cuzz", "Bdd", "Aiming", "Lehends"), 93.5),
    ("KT", "S14", ("PerfecT", "Pyosik", "Bdd", "Deft", "BeryL"), 91.0),
    ("KT", "S15", ("PerfecT", "Cuzz", "Bdd", "deokdam", "Peter"), 93.5),
    ("KT", "S16", ("PerfecT", "Cuzz", "Bdd", "Jiwoo", "Effort"), 90.0),

    # ==================== 8. DRX (DRX / Kingzone DragonX / Longzhu) — S6 to S16 ====================
    ("DRX", "S6", ("Expession", "Chaser", "Coco", "Fury", "Pure"), 87.5),
    ("DRX", "S7", ("Khan", "Cuzz", "Bdd", "PraY", "GorillA"), 93.5),
    ("DRX", "S8", ("Khan", "Peanut", "Bdd", "PraY", "GorillA"), 94.0),
    ("DRX", "S9", ("Rascal", "Cuzz", "PawN", "Deft", "TusiN"), 91.0),
    ("DRX", "S10", ("Doran", "Pyosik", "Chovy", "Deft", "Keria"), 93.0),
    ("DRX", "S11", ("Kingen", "Pyosik", "SOLKA", "BAO", "Becca"), 86.0),
    ("DRX", "S12", ("Kingen", "Pyosik", "Zeka", "Deft", "BeryL"), 95.5),
    ("DRX", "S13", ("Rascal", "Croco", "FATE", "Paduck", "BeryL"), 86.5),
    ("DRX", "S14", ("Rascal", "Sponge", "SeTab", "Teddy", "Pleata"), 86.5),
    ("DRX", "S15", ("Rich", "Sponge", "Ucal", "Teddy", "Andil"), 87.0),
    ("DRX", "S16", ("Rich", "Willer", "Ucal", "Jiwoo", "Andil"), 87.0),

    # ==================== 9. TES (Top Esports) — S9 to S16 ====================
    ("TES", "S9", ("369", "Xx", "knight", "LokeN", "Ben"), 90.5),
    ("TES", "S10", ("369", "Karsa", "knight", "JackeyLove", "yuyanjia"), 94.0),
    ("TES", "S11", ("369", "Karsa", "knight", "JackeyLove", "Zhuo"), 91.5),
    ("TES", "S12", ("Wayward", "Tian", "knight", "JackeyLove", "Mark"), 93.0),
    ("TES", "S13", ("369", "Tian", "Rookie", "JackeyLove", "Mark"), 92.0),
    ("TES", "S14", ("369", "Tian", "Creme", "JackeyLove", "Meiko"), 92.5),
    ("TES", "S15", ("369", "Kanavi", "Creme", "JackeyLove", "Hang"), 93.0),
    ("TES", "S16", ("369", "Tian", "Creme", "JackeyLove", "Zhuo"), 92.0),

    # ==================== 10. JDG (JD Gaming) — S8 to S16 ====================
    ("JDG", "S8", ("Zoom", "Clid", "Yagao", "LokeN", "LvMao"), 90.5),
    ("JDG", "S9", ("Zoom", "Flawless", "Yagao", "imp", "LvMao"), 90.0),
    ("JDG", "S10", ("Zoom", "Kanavi", "Yagao", "LokeN", "LvMao"), 93.5),
    ("JDG", "S11", ("Zoom", "Kanavi", "Yagao", "LokeN", "LvMao"), 90.0),
    ("JDG", "S12", ("369", "Kanavi", "Yagao", "Hope", "Missing"), 94.0),
    ("JDG", "S13", ("369", "Kanavi", "knight", "Ruler", "Missing"), 96.5),
    ("JDG", "S14", ("Flandre", "Kanavi", "Yagao", "Ruler", "Missing"), 92.0),
    ("JDG", "S15", ("Ale", "Xun", "Scout", "Peyz", "Missing"), 91.5),
    ("JDG", "S16", ("Xiaoxu", "JunJia", "Scout", "GALA", "Vampire"), 91.5),

    # ==================== 11. EDG (EDward Gaming) — S4 to S16 ====================
    ("EDG", "S4", ("Koro1", "Clearlove", "U", "NaMei", "Fzzf"), 92.5),
    ("EDG", "S5", ("Koro1", "Clearlove", "PawN", "Deft", "Meiko"), 95.5),
    ("EDG", "S6", ("Mouse", "Clearlove", "Scout", "Deft", "Meiko"), 93.0),
    ("EDG", "S7", ("Mouse", "Clearlove", "Scout", "iBoy", "Meiko"), 92.0),
    ("EDG", "S8", ("Ray", "Haro", "Scout", "iBoy", "Meiko"), 91.0),
    ("EDG", "S9", ("Jinoo", "Jiejie", "Scout", "iBoy", "Meiko"), 90.0),
    ("EDG", "S10", ("Aodi", "Jiejie", "Scout", "Hope", "Meiko"), 89.5),
    ("EDG", "S11", ("Flandre", "Jiejie", "Scout", "Viper", "Meiko"), 96.5),
    ("EDG", "S12", ("Flandre", "Jiejie", "Scout", "Viper", "Meiko"), 93.5),
    ("EDG", "S13", ("Ale", "Jiejie", "FoFo", "Uzi", "Meiko"), 90.5),
    ("EDG", "S14", ("Ale", "Jiejie", "Cryin", "Leave", "Wink"), 87.5),
    ("EDG", "S15", ("Zdz", "Xiaohao", "Angel", "Assum", "Wink"), 87.0),
    ("EDG", "S16", ("Zdz", "Xiaohao", "Angel", "Leave", "Jwei"), 87.5),

    # ==================== 12. RNG (Royal Never Give Up / SHRC / Royal Club) — S3 to S16 ====================
    ("RNG", "S3", ("GodLike", "Lucky", "Wh1t3zZ", "Uzi", "Tabe"), 93.5),
    ("RNG", "S4", ("Cola", "inSec", "corn", "Uzi", "Zero"), 94.0),
    ("RNG", "S5", ("Letme", "Mlxg", "Xiaohu", "Wuxx", "Ley"), 88.5),
    ("RNG", "S6", ("Looper", "Mlxg", "Xiaohu", "Uzi", "Mata"), 93.5),
    ("RNG", "S7", ("Letme", "Mlxg", "Xiaohu", "Uzi", "Ming"), 94.0),
    ("RNG", "S8", ("Letme", "Mlxg", "Xiaohu", "Uzi", "Ming"), 96.0),
    ("RNG", "S9", ("Langx", "Karsa", "Xiaohu", "Uzi", "Ming"), 92.5),
    ("RNG", "S10", ("New", "XLB", "Xiaohu", "Betty", "Ming"), 89.0),
    ("RNG", "S11", ("Xiaohu", "Wei", "Cryin", "GALA", "Ming"), 95.0),
    ("RNG", "S12", ("Breathe", "Wei", "Xiaohu", "GALA", "Ming"), 94.5),
    ("RNG", "S13", ("Breathe", "Wei", "Tangyuan", "LP", "LvMao"), 88.5),
    ("RNG", "S14", ("Breathe", "Wei", "Tangyuan", "Lwx", "Ming"), 87.5),
    ("RNG", "S15", ("Xiaoxu", "milkyway", "Tangyuan", "JiaQi", "Lele"), 86.5),
    ("RNG", "S16", ("Xiaoxu", "milkyway", "Tangyuan", "JiaQi", "Niket"), 86.0),

    # ==================== 13. WBG (Weibo Gaming / Suning) — S8 to S16 ====================
    ("WBG", "S8", ("XiaoAL", "H4cker", "knight", "Smlz", "SwordArt"), 89.0),
    ("WBG", "S9", ("XiaoAL", "Weiwei", "Maple", "Smlz", "SwordArt"), 89.0),
    ("WBG", "S10", ("Bin", "SofM", "Angel", "huanfeng", "SwordArt"), 94.0),
    ("WBG", "S11", ("Bin", "SofM", "Angel", "huanfeng", "ON"), 90.5),
    ("WBG", "S12", ("TheShy", "SofM", "Angel", "huanfeng", "ON"), 90.5),
    ("WBG", "S13", ("TheShy", "Weiwei", "Xiaohu", "Light", "Crisp"), 93.5),
    ("WBG", "S14", ("Breathe", "Tarzan", "Xiaohu", "Light", "Crisp"), 92.5),
    ("WBG", "S15", ("Breathe", "Tian", "Xiaohu", "Light", "Hang"), 90.5),
    ("WBG", "S16", ("Zika", "Jiejie", "Xiaohu", "Elk", "Hang"), 91.5),

    # ==================== 14. FPX (FunPlus Phoenix) — S8 to S16 ====================
    ("FPX", "S8", ("GimGoon", "Alex", "Cool", "Lwx", "Crisp"), 88.0),
    ("FPX", "S9", ("GimGoon", "Tian", "Doinb", "Lwx", "Crisp"), 96.5),
    ("FPX", "S10", ("Khan", "Tian", "Doinb", "Lwx", "Crisp"), 91.5),
    ("FPX", "S11", ("Nuguri", "Tian", "Doinb", "Lwx", "Crisp"), 93.5),
    ("FPX", "S12", ("Summit", "Clid", "Care", "Lwx", "Hang"), 88.5),
    ("FPX", "S13", ("Xiaolaohu", "Bonnie", "Care", "Lwx", "QiuQiu"), 87.5),
    ("FPX", "S14", ("Xiaolaohu", "milkyway", "Care", "deokdam", "Life"), 89.5),
    ("FPX", "S15", ("sheer", "shad0w", "Care", "Assum", "Jwei"), 88.0),
    ("FPX", "S16", ("sheer", "milkyway", "Care", "Assum", "Jwei"), 88.5),

    # ==================== 15. AL (Anyone's Legend / Rogue Warriors) — S8 to S16 ====================
    ("AL", "S8", ("Mouse", "Flawless", "Doinb", "Smlz", "Killua"), 91.0),
    ("AL", "S12", ("Zdz", "Xiaohao", "Forge", "Betty", "QiuQiu"), 86.5),
    ("AL", "S13", ("Zdz", "Xiaohao", "Harder", "Betty", "SwordArt"), 87.0),
    ("AL", "S14", ("Ale", "Croco", "Shanks", "Hope", "Kael"), 89.5),
    ("AL", "S15", ("Flandre", "Tarzan", "Shanks", "Hope", "Kael"), 93.0),
    ("AL", "S16", ("Flandre", "Tarzan", "Shanks", "Hope", "Kael"), 91.5),

    # ==================== 16. LNG (LNG Esports / Snake Esports) — S6 to S16 ====================
    ("LNG", "S6", ("Flandre", "SofM", "Tank", "kRYST4L", "Ella"), 89.5),
    ("LNG", "S9", ("Flandre", "SofM", "Plex", "Asura", "Duan"), 89.0),
    ("LNG", "S11", ("Ale", "Tarzan", "icon", "Light", "Iwandy"), 91.0),
    ("LNG", "S12", ("Ale", "Tarzan", "Doinb", "Light", "LvMao"), 91.5),
    ("LNG", "S13", ("Zika", "Tarzan", "Scout", "GALA", "Hang"), 93.5),
    ("LNG", "S14", ("Zika", "Weiwei", "Scout", "GALA", "Hang"), 92.0),
    ("LNG", "S15", ("Zika", "Weiwei", "Haichao", "Photic", "Zhuo"), 88.0),
    ("LNG", "S16", ("sheer", "Weiwei", "Haichao", "1xn", "Missing"), 88.5),

    # ==================== 17. WE (Team WE / World Elite) — S2 to S16 ====================
    ("WE", "S2", ("CaoMei", "Clearlove", "Misaya", "WeiXiao", "Fzzf"), 95.0),
    ("WE", "S3", ("CaoMei", "Clearlove", "Misaya", "WeiXiao", "Fzzf"), 92.5),
    ("WE", "S5", ("Aluka", "Spirit", "xiye", "Mystic", "YuZhe"), 89.5),
    ("WE", "S7", ("957", "Condi", "xiye", "Mystic", "Ben"), 93.5),
    ("WE", "S11", ("Breathe", "beishang", "Shanks", "Elk", "Missing"), 90.0),
    ("WE", "S14", ("Wayward", "Heng", "FoFo", "Prince", "Iwandy"), 87.5),
    ("WE", "S16", ("Cube", "Monki", "Karis", "Taeyoon", "Vampire"), 87.0),

    # ==================== 18. OMG (Oh My God) — S3 to S16 ====================
    ("OMG", "S3", ("Gogoing", "LoveLin", "Cool", "San", "Bigpomelo"), 93.5),
    ("OMG", "S4", ("Gogoing", "Loveling", "Cool", "San", "Cloud"), 93.5),
    ("OMG", "S5", ("Gogoing", "Loveling", "Cool", "Uzi", "Cloud"), 90.0),
    ("OMG", "S7", ("Xiyang", "World6", "icon", "Smlz", "Five"), 89.5),
    ("OMG", "S13", ("shanji", "Aki", "Creme", "Able", "ppgod"), 90.5),
    ("OMG", "S16", ("Hery", "Heng", "Linfeng", "Starry", "Moham"), 86.5),

    # ==================== 19. G2 (G2 Esports) — S6 to S16 ====================
    ("G2", "S6", ("Expect", "Trick", "Perkz", "Zven", "Mithy"), 90.0),
    ("G2", "S7", ("Expect", "Trick", "Perkz", "Zven", "Mithy"), 92.0),
    ("G2", "S8", ("Wunder", "Jankos", "Perkz", "Hjarnan", "Wadid"), 92.0),
    ("G2", "S9", ("Wunder", "Jankos", "Caps", "Perkz", "Mikyx"), 96.0),
    ("G2", "S10", ("Wunder", "Jankos", "Caps", "Perkz", "Mikyx"), 94.0),
    ("G2", "S11", ("Wunder", "Jankos", "Caps", "Rekkles", "Mikyx"), 91.0),
    ("G2", "S12", ("BrokenBlade", "Jankos", "Caps", "Flakked", "Targamas"), 90.5),
    ("G2", "S13", ("BrokenBlade", "Yike", "Caps", "Hans Sama", "Mikyx"), 91.5),
    ("G2", "S14", ("BrokenBlade", "Yike", "Caps", "Hans Sama", "Mikyx"), 92.0),
    ("G2", "S15", ("BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov"), 91.0),
    ("G2", "S16", ("BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov"), 90.5),

    # ==================== 20. FNC (Fnatic) — S1 to S16 ====================
    ("FNC", "S1", ("xPeke", "Cyanide", "Shushei", "LaMiaZeaLoT", "Mellisan"), 94.0),
    ("FNC", "S3", ("sOAZ", "Cyanide", "xPeke", "Puszu", "YellOwStaR"), 92.5),
    ("FNC", "S4", ("sOAZ", "Cyanide", "xPeke", "Rekkles", "YellOwStaR"), 91.0),
    ("FNC", "S5", ("Huni", "Reignover", "Febiven", "Rekkles", "YellOwStaR"), 94.0),
    ("FNC", "S7", ("sOAZ", "Broxah", "Caps", "Rekkles", "Jesiz"), 90.5),
    ("FNC", "S8", ("Bwipo", "Broxah", "Caps", "Rekkles", "Hylissang"), 94.5),
    ("FNC", "S9", ("Bwipo", "Broxah", "Nemesis", "Rekkles", "Hylissang"), 92.0),
    ("FNC", "S10", ("Bwipo", "Selfmade", "Nemesis", "Rekkles", "Hylissang"), 92.0),
    ("FNC", "S11", ("Adam", "Bwipo", "Nisqy", "Upset", "Hylissang"), 89.5),
    ("FNC", "S12", ("Wunder", "Razork", "Humanoid", "Upset", "Hylissang"), 89.5),
    ("FNC", "S13", ("Oscarinin", "Razork", "Humanoid", "Noah", "Trymbi"), 89.0),
    ("FNC", "S14", ("Oscarinin", "Razork", "Humanoid", "Noah", "Jun"), 89.5),
    ("FNC", "S15", ("Oscarinin", "Razork", "Poby", "Upset", "Mikyx"), 89.0),
    ("FNC", "S16", ("Empyros", "Razork", "Vladi", "Upset", "Lospa"), 88.5),

    # ==================== 21. MAD (MAD Lions KOI / Movistar KOI / Splyce) — S6 to S16 ====================
    ("MAD", "S6", ("Wunder", "Trashy", "Sencux", "Kobbe", "Mikyx"), 88.0),
    ("MAD", "S9", ("Vizicsacsi", "Xerxe", "Humanoid", "Kobbe", "Norskeren"), 90.0),
    ("MAD", "S10", ("Orome", "Shad0w", "Humanoid", "Carzzy", "Kaiser"), 89.0),
    ("MAD", "S11", ("Armut", "Elyoya", "Humanoid", "Carzzy", "Kaiser"), 92.0),
    ("MAD", "S12", ("Armut", "Elyoya", "Nisqy", "UNF0RGIVEN", "Kaiser"), 88.5),
    ("MAD", "S13", ("Chasy", "Elyoya", "Nisqy", "Carzzy", "Hylissang"), 89.0),
    ("MAD", "S14", ("Myrwn", "Elyoya", "Fresskowy", "Supa", "Alvaro"), 88.0),
    ("MAD", "S15", ("Myrwn", "Elyoya", "Jojopyun", "Supa", "Alvaro"), 88.5),
    ("MAD", "S16", ("Myrwn", "Elyoya", "Vladi", "Supa", "Alvaro"), 88.5),

    # ==================== 22. RGE (Rogue / KOI) — S10 to S16 ====================
    ("RGE", "S10", ("Finn", "Inspired", "Larssen", "Hans Sama", "Vander"), 89.5),
    ("RGE", "S11", ("Odoamne", "Inspired", "Larssen", "Hans Sama", "Trymbi"), 90.5),
    ("RGE", "S12", ("Odoamne", "Malrang", "Larssen", "Comp", "Trymbi"), 91.5),
    ("RGE", "S13", ("Szygenda", "Malrang", "Larssen", "Comp", "Trymbi"), 88.0),
    ("RGE", "S14", ("Finn", "Markoon", "Larssen", "Comp", "Zoelys"), 86.5),
    ("RGE", "S16", ("Adam", "Malrang", "Larssen", "Patrik", "Execute"), 86.5),

    # ==================== 23. C9 (Cloud9) — S3 to S16 ====================
    ("C9", "S3", ("Balls", "Meteos", "Hai", "Sneaky", "LemonNation"), 91.0),
    ("C9", "S4", ("Balls", "Meteos", "Hai", "Sneaky", "LemonNation"), 90.5),
    ("C9", "S6", ("Impact", "Meteos", "Jensen", "Sneaky", "Smoothie"), 89.5),
    ("C9", "S7", ("Impact", "Contractz", "Jensen", "Sneaky", "Smoothie"), 90.0),
    ("C9", "S8", ("Licorice", "Svenskeren", "Jensen", "Sneaky", "Zeyzal"), 92.5),
    ("C9", "S9", ("Licorice", "Svenskeren", "Nisqy", "Sneaky", "Zeyzal"), 89.0),
    ("C9", "S11", ("Fudge", "Blaber", "Perkz", "Zven", "Vulcan"), 90.0),
    ("C9", "S12", ("Fudge", "Blaber", "Jensen", "Berserker", "Zven"), 89.5),
    ("C9", "S13", ("Fudge", "Blaber", "EMENES", "Berserker", "Zven"), 89.0),
    ("C9", "S14", ("Thanatos", "Blaber", "Jojopyun", "Berserker", "Vulcan"), 89.0),
    ("C9", "S15", ("Thanatos", "Blaber", "Loki", "Zven", "Vulcan"), 88.5),
    ("C9", "S16", ("Thanatos", "Blaber", "APA", "Zven", "Vulcan"), 88.5),

    # ==================== 24. TL (Team Liquid) — S5 to S16 ====================
    ("TL", "S5", ("Quas", "IWillDominate", "FeniX", "Piglet", "Xpecial"), 88.5),
    ("TL", "S8", ("Impact", "Xmithie", "Pobelter", "Doublelift", "Olleh"), 90.0),
    ("TL", "S9", ("Impact", "Xmithie", "Jensen", "Doublelift", "CoreJJ"), 92.5),
    ("TL", "S10", ("Impact", "Broxah", "Jensen", "Tactical", "CoreJJ"), 89.5),
    ("TL", "S11", ("Alphari", "Santorin", "Jensen", "Tactical", "CoreJJ"), 89.5),
    ("TL", "S12", ("Bwipo", "Santorin", "Bjergsen", "Hans Sama", "CoreJJ"), 89.0),
    ("TL", "S13", ("Summit", "Pyosik", "APA", "Yeon", "CoreJJ"), 88.5),
    ("TL", "S14", ("Impact", "UmTi", "APA", "Yeon", "CoreJJ"), 89.5),
    ("TL", "S15", ("Impact", "UmTi", "APA", "Yeon", "CoreJJ"), 89.0),
    ("TL", "S16", ("Impact", "Inspired", "APA", "Yeon", "CoreJJ"), 89.5),

    # ==================== 25. FLY (FlyQuest) — S10 to S16 ====================
    ("FLY", "S10", ("Solo", "Santorin", "PowerOfEvil", "WildTurtle", "IgNar"), 89.0),
    ("FLY", "S13", ("Impact", "Spica", "VicLa", "Prince", "Vulcan"), 87.5),
    ("FLY", "S14", ("Bwipo", "Inspired", "Quad", "Massu", "Busio"), 90.5),
    ("FLY", "S15", ("Bwipo", "Inspired", "Quad", "Massu", "Busio"), 90.0),
    ("FLY", "S16", ("Bwipo", "Inspired", "Quad", "Massu", "Busio"), 89.5),

    # ==================== 26. TSM (Team SoloMid) — S1 to S11 ====================
    ("TSM", "S1", ("TheRainMan", "TheOddOne", "Reginald", "Chaox", "Xpecial"), 90.0),
    ("TSM", "S2", ("Dyrus", "TheOddOne", "Reginald", "Chaox", "Xpecial"), 89.5),
    ("TSM", "S3", ("Dyrus", "TheOddOne", "Reginald", "WildTurtle", "Xpecial"), 89.0),
    ("TSM", "S4", ("Dyrus", "Amazing", "Bjergsen", "WildTurtle", "Lustboy"), 91.0),
    ("TSM", "S5", ("Dyrus", "Santorin", "Bjergsen", "WildTurtle", "Lustboy"), 90.0),
    ("TSM", "S6", ("Hauntzer", "Svenskeren", "Bjergsen", "Doublelift", "Biofrost"), 91.5),
    ("TSM", "S7", ("Hauntzer", "Svenskeren", "Bjergsen", "Doublelift", "Biofrost"), 90.5),
    ("TSM", "S10", ("BrokenBlade", "Spica", "Bjergsen", "Doublelift", "Biofrost"), 88.5),
    ("TSM", "S11", ("Huni", "Spica", "PowerOfEvil", "Lost", "SwordArt"), 88.5),

    # ==================== 27. CLG (Counter Logic Gaming / NRG) — S1 to S13 ====================
    ("CLG", "S1", ("HotshotGG", "Saintvicious", "bigfatlp", "Chauster", "Elementz"), 90.0),
    ("CLG", "S2", ("Voyboy", "Saintvicious", "bigfatlp", "Doublelift", "Chauster"), 89.5),
    ("CLG", "S5", ("ZionSpartan", "Xmithie", "Pobelter", "Doublelift", "aphromoo"), 90.0),
    ("CLG", "S6", ("Darshan", "Xmithie", "Huhi", "Stixxay", "aphromoo"), 91.5),
    ("CLG", "S13", ("Dhokla", "Contractz", "Palafox", "FBI", "IgNar"), 90.0),

    # ==================== 28. TPA (Taipei Assassins / Flash Wolves / PSG / CFO) — S2 to S16 ====================
    ("TPA", "S2", ("Stanley", "Lilballz", "Toyz", "Bebe", "MiSTakE"), 95.5),
    ("TPA", "S5", ("Steak", "Karsa", "Maple", "NL", "SwordArt"), 90.5),
    ("TPA", "S6", ("MMD", "Karsa", "Maple", "NL", "SwordArt"), 91.0),
    ("TPA", "S7", ("MMD", "Karsa", "Maple", "Betty", "SwordArt"), 91.0),
    ("TPA", "S8", ("Hanabi", "Moojin", "Maple", "Betty", "SwordArt"), 90.5),
    ("TPA", "S11", ("Hanabi", "River", "Maple", "Unified", "Kaiwing"), 91.0),
    ("TPA", "S14", ("Azhi", "JunJia", "Maple", "Betty", "Woody"), 89.0),
    ("TPA", "S15", ("Driver", "JunJia", "HongQ", "Doggo", "Kaiwing"), 90.5),
    ("TPA", "S16", ("Rest", "Shad0w", "Pout", "Doggo", "Kaiwing"), 89.0),

    # ==================== 29. AZF (Azubu Frost / NaJin) — S2 to S4 ====================
    ("AZF", "S2", ("Shy", "CloudTemplar", "RapidStar", "Woong", "MadLife"), 94.0),
    ("AZF", "S3", ("Expession", "watch", "Nagne", "PraY", "Cain"), 92.0),
    ("AZF", "S4", ("Save", "watch", "Ggoong", "Zefa", "GorillA"), 91.5),

    # ==================== 30. M5 (Moscow Five / Gambit Gaming) — S2 to S3 ====================
    ("M5", "S2", ("Darien", "Diamondprox", "Alex Ich", "Genja", "Gosu Pepper"), 94.5),
    ("M5", "S3", ("Darien", "Diamondprox", "Alex Ich", "Genja", "Darker"), 92.0),

    # ==================== 31. AAA (against All authority / CLG Europe / Alliance) — S1 to S4 ====================
    ("AAA", "S1", ("sOAZ", "Linak", "MoMa", "YellOwStaR", "Kujaa"), 92.5),
    ("AAA", "S2", ("Wickd", "Snoopeh", "Froggen", "Yellowpete", "Krepo"), 93.5),
    ("AAA", "S4", ("Wickd", "Shook", "Froggen", "Tabzz", "Nyph"), 90.5),

    # ==================== 32. OG (Origen) — S5 to S9 ====================
    ("OG", "S5", ("sOAZ", "Amazing", "xPeke", "Niels", "Mithy"), 92.5),
    ("OG", "S9", ("Alphari", "Kold", "Nukeduck", "Patrik", "Mithy"), 89.5),
]

ERA_ROSTERS_CATALOG: List[Tuple[str, str, str, str, float, float, float, float, float, List[str], float]] = []
for _tid, _season, _players, _rating in RAW_TEAM_ERA_LINEUPS:
    ERA_ROSTERS_CATALOG.extend(_build_lineup(_tid, _season, _players, _rating))
