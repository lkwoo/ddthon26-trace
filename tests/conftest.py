"""Shared pytest / Hypothesis configuration.

Reproducibility (PBT-08): shrinking stays enabled (never disabled), and failing
examples print a reproducible blob. Set ``HYPOTHESIS_PROFILE=ci`` for a
deterministic derandomized run in CI; the default profile logs seeds on failure.
"""

import os

from hypothesis import HealthCheck, Verbosity, settings

settings.register_profile("dev", print_blob=True, verbosity=Verbosity.normal)
settings.register_profile(
    "ci",
    print_blob=True,
    derandomize=True,  # fixed, reproducible run in CI
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
