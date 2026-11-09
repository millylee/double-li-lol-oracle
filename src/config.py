import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MAPPING_DIR = DATA_DIR / "mapping"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
MAPPING_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("LOL_DB_PATH", str(DATA_DIR / "lol_esports.db")))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH

TEAM_ALIASES_PATH = MAPPING_DIR / "team_aliases.json"

LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

LEAGUEPEDIA_API_URL = "https://lol.fandom.com/api.php"
LEAGUEPEDIA_USER_AGENT = os.getenv(
    "LEAGUEPEDIA_USER_AGENT",
    "LoLMVPPredictor/1.0 (Esports Historical Research & Analytics)"
)

# Regional base Elo & multiplier configuration
REGION_BASE_ELO = {
    "LCK": 1560.0,
    "LPL": 1545.0,
    "LEC": 1465.0,
    "LCS": 1435.0,
    "PCS": 1420.0,
    "OTHER": 1380.0,
}

SEASON_YEAR_MAP = {
    f"S{i}": 2010 + i for i in range(1, 17)
}
YEAR_SEASON_MAP = {v: k for k, v in SEASON_YEAR_MAP.items()}
