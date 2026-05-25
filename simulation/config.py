from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent / "data" / "runs"

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
MEDIATION_FEE = 1
DEFAULT_BREACH_PENALTY = 6   # 2x utility value of one unit

# Governance mechanism parameters
GOV_ORACLE_WINDOW = 5
GOV_DEFECTION_THRESHOLD = 0.40
GOV_PRODUCTION_THRESHOLD = 0.50
GOV_PRODUCTION_CONSEC = 3
GOV_TRADE_VOLUME_MIN = 2
GOV_PREDATORY_THRESHOLD = 3
GOV_FINE_SCHEDULE = {1: 2, 2: 4, 3: 6}
GOV_SUSPENSION_DURATION = 3
GOV_WARNING_EXPIRY = 2
GOV_CLEAN_ROUNDS_TO_DEESCALATE = 2

# Network Rewiring mechanism parameters
NET_MAX_SEVER_PER_ROUND = 3
NET_MAX_REQUEST_PER_ROUND = 3

# Marketplace cooperation threshold (Sustainability and Peace must exceed this)
COOPERATION_THRESHOLD = 0.5

# LLM — simulation agents (GPT)
AZURE_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/openai/v1"
MODEL = "gpt-5.4-mini-BQ-Cohort"

# LLM — analyst agent (Claude)
ANALYST_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/anthropic"
ANALYST_MODEL = "claude-opus-4-6-BQ-Cohort"
MAX_RETRIES = 6       # retries per agent call (handles rate limits with 18 agents)

# Agent reasoning style: all agents use chain-of-thought (CoopEval CoTAgent pattern)
COT_AGENT_IDS = set(range(18))   # all agents

# Network structure
MIN_NEIGHBORS = 7
MAX_NEIGHBORS = 9

# Experimental conditions (2^4 factorial: R, C, M, G)
CONDITIONS = [
    "B", "R", "C", "M", "G", "N", "NR",
    # Combinations (disabled for initial test runs):
    # "RC", "RM", "RG", "CM", "CG", "MG",
    # "RCM", "RCG", "RMG", "CMG",
    # "RCMG",
]

CONDITION_MECHANISMS = {
    "B":    [],
    "R":    ["reputation"],
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
    "N":    ["network_rewiring"],
    "NR":   ["network_rewiring", "reputation"],
}
