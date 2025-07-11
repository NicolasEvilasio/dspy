import logging
import os
from pathlib import Path
from typing import Optional

import litellm

# Try to import LiteLLM cache from different possible locations
try:
    from litellm.caching.caching import Cache as LitellmCache
except ImportError:
    try:
        from litellm.caching import Cache as LitellmCache
    except ImportError:
        try:
            from litellm import Cache as LitellmCache
        except ImportError:
            # If no cache is available, create a dummy class
            class LitellmCache:
                """Dummy cache for compatibility when LiteLLM caching is not available"""
                def __init__(self, *args, **kwargs):
                    pass

from dspy.clients.base_lm import BaseLM, inspect_history
from dspy.clients.cache import Cache
from dspy.clients.embedding import Embedder
from dspy.clients.lm import LM
from dspy.clients.provider import Provider, TrainingJob

logger = logging.getLogger(__name__)

DISK_CACHE_DIR = os.environ.get("DSPY_CACHEDIR") or os.path.join(Path.home(), ".dspy_cache")
DISK_CACHE_LIMIT = int(os.environ.get("DSPY_CACHE_LIMIT", 3e10))  # 30 GB default


def _litellm_track_cache_hit_callback(kwargs, completion_response, start_time, end_time):
    # Access the cache_hit information
    completion_response.cache_hit = kwargs.get("cache_hit", False)


litellm.success_callback = [_litellm_track_cache_hit_callback]


def configure_cache(
    enable_disk_cache: bool | None = True,
    enable_memory_cache: bool | None = True,
    disk_cache_dir: str | None = DISK_CACHE_DIR,
    disk_size_limit_bytes: int | None = DISK_CACHE_LIMIT,
    memory_max_entries: int | None = 1000000,
    enable_litellm_cache: bool = False,
):
    """Configure the cache for DSPy.

    Args:
        enable_disk_cache: Whether to enable on-disk cache.
        enable_memory_cache: Whether to enable in-memory cache.
        disk_cache_dir: The directory to store the on-disk cache.
        disk_size_limit_bytes: The size limit of the on-disk cache.
        memory_max_entries: The maximum number of entries in the in-memory cache.
        enable_litellm_cache: Whether to enable LiteLLM cache.
    """
    if enable_disk_cache and enable_litellm_cache:
        raise ValueError(
            "Cannot enable both LiteLLM and DSPy on-disk cache, please set at most one of `enable_disk_cache` or "
            "`enable_litellm_cache` to True."
        )

    if enable_litellm_cache:
        try:
            litellm.cache = LitellmCache(disk_cache_dir=DISK_CACHE_DIR, type="disk")

            if litellm.cache.cache.disk_cache.size_limit != DISK_CACHE_LIMIT:
                litellm.cache.cache.disk_cache.reset("size_limit", DISK_CACHE_LIMIT)
        except Exception as e:
            # It's possible that users don't have the write permissions to the cache directory.
            # In that case, we'll just disable the cache.
            logger.warning("Failed to initialize LiteLLM cache: %s", e)
            litellm.cache = None
    else:
        litellm.cache = None

    import dspy

    dspy.cache = Cache(
        enable_disk_cache,
        enable_memory_cache,
        disk_cache_dir,
        disk_size_limit_bytes,
        memory_max_entries,
    )


litellm.telemetry = False
litellm.cache = None  # By default we disable litellm cache and use DSPy on-disk cache.

DSPY_CACHE = Cache(
    enable_disk_cache=True,
    enable_memory_cache=True,
    disk_cache_dir=DISK_CACHE_DIR,
    disk_size_limit_bytes=DISK_CACHE_LIMIT,
    memory_max_entries=1000000,
)

# Turn off by default to avoid LiteLLM logging during every LM call.
litellm.suppress_debug_info = True

if "LITELLM_LOCAL_MODEL_COST_MAP" not in os.environ:
    # Accessed at run time by litellm; i.e., fine to keep after import
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"


def enable_litellm_logging():
    litellm.suppress_debug_info = False


def disable_litellm_logging():
    litellm.suppress_debug_info = True


__all__ = [
    "BaseLM",
    "LM",
    "Provider",
    "TrainingJob",
    "inspect_history",
    "Embedder",
    "enable_litellm_logging",
    "disable_litellm_logging",
    "configure_cache",
]
