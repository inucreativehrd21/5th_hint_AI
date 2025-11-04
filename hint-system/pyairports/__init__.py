"""Local shim for missing `pyairports` PyPI package.

This project previously saw a broken pyairports package on PyPI (0.0.1) which
caused import errors inside `outlines`. To avoid runtime crashes during vLLM
startup we provide a tiny local shim that exposes the minimal symbol
`AIRPORT_LIST` used by outlines. This avoids network installs and keeps the
process local and deterministic.

The shim intentionally contains a minimal empty dataset. If you need full
airport data features, replace this with the real data or install a proper
package (e.g., `airportsdata`) and adapt outlines usage.
"""

from .airports import AIRPORT_LIST
