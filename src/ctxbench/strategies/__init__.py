from ctxbench.strategies.full_history import FullHistory
from ctxbench.strategies.hybrid import Hybrid
from ctxbench.strategies.masking import ObservationMasking
from ctxbench.strategies.summarization import LLMSummarization

STRATEGIES = {
    "full_history": lambda llm: FullHistory(),
    "masking": lambda llm: ObservationMasking(),
    "summarization": lambda llm: LLMSummarization(llm),
    "hybrid": lambda llm: Hybrid(llm),
}
