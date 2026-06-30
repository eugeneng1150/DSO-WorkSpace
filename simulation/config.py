from pathlib import Path

# Paths
_BASE_DATA_DIR = Path(__file__).parent / "data" / "runs"
DATA_DIR = _BASE_DATA_DIR / "gpt-5.4-mini"  # default; call set_model_tag() to override


def set_model_tag(tag: str):
    """Set DATA_DIR to _BASE_DATA_DIR / tag so each model gets its own log folder."""
    global DATA_DIR
    DATA_DIR = _BASE_DATA_DIR / tag

# Market structure
GOODS = ["A", "B", "C"]
N_AGENTS = 18         # 6 per good
AGENTS_PER_GOOD = 6

# Utility values
UTILITY_CONSUME = 3   # per unit of needed good consumed
COST_PRODUCE = 1      # utility per unit produced (deducted at consumption)
MAX_PRODUCE = 5       # per round
SPOILAGE_RATE = 0.2   # 20% of held inventory lost per round (perishable goods)

# Simulation parameters
ROUNDS = 30
RUNS_PER_CONDITION = 3
MEMORY_WINDOW = 5     # rounds of partner history shown to agent

# Mechanism parameters
MEDIATION_FEE = 0
DEFAULT_BREACH_PENALTY = 6   # 2x utility value of one unit

# Governance mechanism parameters
GOV_ORACLE_WINDOW = 5
GOV_DEFECTION_THRESHOLD = 0.40
GOV_PREDATORY_THRESHOLD = 3
GOV_FINE_SCHEDULE = {1: 2, 2: 4, 3: 6}
GOV_SUSPENSION_DURATION = 3
GOV_WARNING_EXPIRY = 2
GOV_CLEAN_ROUNDS_TO_DEESCALATE = 2

# Network Rewiring mechanism parameters
NET_MAX_SEVER_PER_ROUND = 99
NET_MAX_REQUEST_PER_ROUND = 99

# Sanction mechanism parameters
SANCTION_COST_RATIO = 3   # spend 1 utility → target loses 3

# Judicial mechanism parameters
JUDICIAL_FILING_FEE = 1        # cost to file a complaint (paid regardless)
JUDICIAL_PENALTY = 5           # fine on guilty defector
JUDICIAL_COMPENSATION = 3      # returned to victim on guilty verdict
JUDICIAL_FALSE_FINE = 2        # additional fine for false/invalid complaint

# Escrow mechanism parameters
ESCROW_POOL_INITIAL = 1000     # shared insurance pool starting balance
ESCROW_PAYOUT = 4              # compensation paid from pool to victim per defection

# Progressive troll injection schedule: list of (round, n_new_trolls)
# Empty list = no progressive injection (use --trolls for fixed count)
TROLL_SCHEDULE: list[tuple[int, int]] = []

# Marketplace cooperation threshold (Sustainability and Cooperation Rate must exceed this)
COOPERATION_THRESHOLD = 0.5

# LLM — simulation agents (GPT via Azure, default)
AZURE_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/openai/v1"
MODEL = "gpt-5.4-mini-BQ-Cohort"

# LLM — GPT-5.4-nano via Azure (same endpoint)
NANO_MODEL = "gpt-5.4-nano-BQ-Cohort"

# LLM — DeepSeek-V3.2 via Azure
DEEPSEEK_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/openai/v1"
DEEPSEEK_MODEL = "DeepSeek-V3.2-BQ-Cohort"

# LLM — local Docker (oss-120b via llama.cpp)
DOCKER_ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1"
DOCKER_MODEL = "hf.co/unsloth/gpt-oss-120b-GGUF:Q4_K_M"
DOCKER_API_KEY = "local"

# LLM — local Docker (oss-20b via llama.cpp)
OSS20B_ENDPOINT = "http://localhost:8080/v1"
OSS20B_MODEL = "gpt-oss-20b-Q8_0.gguf"
OSS20B_API_KEY = "local"

# LLM — analyst agent (Claude)
ANALYST_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.services.ai.azure.com/anthropic/"
ANALYST_MODEL = "claude-opus-4-8-BQ-Cohort"
MAX_RETRIES = 8       # retries per agent call (handles rate limits with 18+ agents)

# Agent reasoning style: all agents use chain-of-thought (CoopEval CoTAgent pattern)
COT_AGENT_IDS = set(range(18))   # all agents

# Network structure
MIN_NEIGHBORS = 7
MAX_NEIGHBORS = 99

# Experimental conditions
MESSAGE_HISTORY_WINDOW = 10  # rounds of public message history for local reputation (gossip)

# Experimental conditions
CONDITIONS = [
    "B", "GR", "C", "M", "G", "NR", "S", "J",
    # Combinations (disabled for initial test runs):
    # "RC", "RM", "RG", "CM", "CG", "MG",
    # "RCM", "RCG", "RMG", "CMG",
    # "RCMG",
]

CONDITION_MECHANISMS = {
    "B":    [],
    "GR":   ["reputation"],
    "R":    ["reputation"],  # removed from CONDITIONS; kept for loading old R_run_*.json logs
    "C":    ["contracting"],
    "M":    ["mediation"],
    "G":    ["governance"],
    "RC":   ["reputation", "contracting"],
    "RM":   ["reputation", "mediation"],
    "RG":   ["reputation", "governance"],
    "CM":   ["contracting", "mediation"],
    "CG":   ["contracting", "governance"],
    "MG":   ["mediation", "governance"],
    "RCM":  ["reputation", "contracting", "mediation"],
    "RCG":  ["reputation", "contracting", "governance"],
    "RMG":  ["reputation", "mediation", "governance"],
    "CMG":  ["contracting", "mediation", "governance"],
    "RCMG": ["reputation", "contracting", "mediation", "governance"],
    "M_SAC": ["mediation", "sac"],
    "N":    ["network_rewiring"],  # removed from CONDITIONS; kept here for loading old N_run_*.json logs
    "NR":   ["network_rewiring", "local_reputation"],
    "S":    ["sanction"],
    "J":    ["judicial"],
    "E":    ["escrow"],
}
