import inspect

from ctxbench.strategies.base import ContextStrategy
from ctxbench.strategies.full_history import FullHistory
from ctxbench.strategies.hybrid import HybridMaskingSummarization
from ctxbench.strategies.masking import ObservationMasking
from ctxbench.strategies.summarization import LLMSummarization

# Add new strategies here.
REGISTRY: dict[str, type[ContextStrategy]] = {
    "full_history": FullHistory,
    "masking": ObservationMasking,  # Assignment A
    "summarization": LLMSummarization,  # Assignment B
    "hybrid": HybridMaskingSummarization,  # Assignment C
}


def make_strategy(name: str, llm=None, **params) -> ContextStrategy:
    """Build a strategy by name. Strategies whose constructor takes `llm` get one."""
    cls = REGISTRY[name]
    if "llm" in inspect.signature(cls.__init__).parameters:
        return cls(llm=llm, **params)
    return cls(**params)


__all__ = ["REGISTRY", "make_strategy", "ContextStrategy"]
