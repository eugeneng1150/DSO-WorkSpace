from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = Path(__file__).parent / "data" / "runs"

# Market structure
GOODS = ["A", "B", "C"]
N_AGENTS = 9          # 3 per good
AGENTS_PER_GOOD = 3

# Utility values
UTILITY_CONSUME = 3   # per unit of needed good consumed
COST_PRODUCE = 1      # per unit produced
MAX_PRODUCE = 5       # per round

# Simulation parameters
ROUNDS = 30
RUNS_PER_CONDITION = 10
MEMORY_WINDOW = 5     # rounds of partner history shown to agent

# Mechanism parameters
MEDIATION_FEE = 1
DEFAULT_BREACH_PENALTY = 6   # 2x utility value of one unit

# Stability threshold (all metrics must exceed this)
STABILITY_THRESHOLD = 0.5

# LLM
AZURE_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/openai/v1"
MODEL = "gpt-5.4-nano-BQ-Cohort"
MAX_RETRIES = 3       # JSON parse retries per agent call

# Agent reasoning style: all agents use chain-of-thought (CoopEval CoTAgent pattern)
COT_AGENT_IDS = {0, 1, 2, 3, 4, 5, 6, 7, 8}   # all agents

# Experimental conditions
CONDITIONS = ["B", "R", "C", "M", "RC", "CM", "RCM"]

CONDITION_MECHANISMS = {
    "B":   [],
    "R":   ["reputation"],
    "C":   ["contracting"],
    "M":   ["mediation"],
    "RC":  ["reputation", "contracting"],
    "CM":  ["contracting", "mediation"],
    "RCM": ["reputation", "contracting", "mediation"],
}
