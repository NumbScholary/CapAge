"""Future-clock verification for phase-one clock injection (scratch, not committed).

Forces the *default* system clock in each of the three fixed runners far past
the frozen tariff expiry (2027-06-01), then re-runs their existing test suites
under that patched default. Every tariff-path test now injects its own clock,
so a green run proves no test still falls through to the real wall clock; the
two intentional expiry tests inject their own expired clock and pass on their
own terms.

Run: python3 -m unittest tests.future_clock_verify
"""

from datetime import datetime, timezone

import capage.homeostasis_active_runner as m1
import capage.homeostasis_v2_active_runner as m2
import capage.homeostasis_v2_replication_runner as m3

# Import the existing TestCase classes so unittest discovers and runs them here.
from tests.test_homeostasis_active_runner import *  # noqa: F401,F403
from tests.test_homeostasis_v2_active_runner import *  # noqa: F401,F403
from tests.test_homeostasis_v2_replication_runner import *  # noqa: F401,F403

_FUTURE = datetime(2027, 6, 1, tzinfo=timezone.utc)


def _future_clock():
    return _FUTURE


def setUpModule():
    # Point every runner's no-clock default at a far-future instant. Tests that
    # inject their own clock are unaffected; any test that forgot to would now
    # observe an expired tariff and fail here.
    #
    # NB: the injection seam committed in c7385c2 is the module-level ``_utc_now``
    # (routed through ``self._now``), not ``_system_clock``. Patching the wrong
    # symbol would silently no-op and make this whole verification vacuous.
    m1._utc_now = _future_clock
    m2._utc_now = _future_clock
    m3._utc_now = _future_clock
