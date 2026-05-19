from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = Path(__file__).parent / "data" / "runs"

# Market structure
GOODS = ["A", "B", "C"]
N_AGENTS = 18         # 6 per good
AGENTS_PER_GOOD = 6

# Utility values
UTILITY_CONSUME = 3   # per unit of needed good consumed
COST_PRODUCE = 1      # tokens per unit produced
MAX_PRODUCE = 5       # per round
STARTING_TOKENS = 20  # initial budget per agent
ROUND_INCOME = 3      # tokens granted to each agent per round (prevents deflationary collapse)
FAIR_PRICE = 2        # suggested fair token price per unit
SPOILAGE_RATE = 0.2   # 20% of held inventory lost per round (perishable goods)

# Simulation parameters
ROUNDS = 30
RUNS_PER_CONDITION = 15
MEMORY_WINDOW = 5     # rounds of partner history shown to agent

# Mechanism parameters
MEDIATION_FEE = 1
DEFAULT_BREACH_PENALTY = 6   # 2x utility value of one unit

# Marketplace cooperation threshold (Sustainability and Peace must exceed this)
COOPERATION_THRESHOLD = 0.5

# LLM — simulation agents (GPT)
AZURE_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/openai/v1"
MODEL = "gpt-5.4-nano-BQ-Cohort"

# LLM — analyst agent (Claude)
ANALYST_ENDPOINT = "https://info-bq-mass-cohort-api-keys-finalv1.openai.azure.com/anthropic"
ANALYST_MODEL = "claude-opus-4-6-BQ-Cohort"
MAX_RETRIES = 6       # retries per agent call (handles rate limits with 18 agents)

# Agent reasoning style: all agents use chain-of-thought (CoopEval CoTAgent pattern)
COT_AGENT_IDS = set(range(18))   # all agents

# Network structure
MIN_NEIGHBORS = 7
MAX_NEIGHBORS = 9

# Experimental conditions
CONDITIONS = ["B", "R", "C", "M", "RC", "RM", "CM", "RCM"]

CONDITION_MECHANISMS = {
    "B":   [],
    "R":   ["reputation"],
    "C":   ["contracting"],
    "M":   ["mediation"],
    "RC":  ["reputation", "contracting"],
    "RM":  ["reputation", "mediation"],
    "CM":  ["contracting", "mediation"],
    "RCM": ["reputation", "contracting", "mediation"],
}
