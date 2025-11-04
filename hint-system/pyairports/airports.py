"""Minimal airports data shim used only to satisfy `outlines` import.

This provides a tiny, safe placeholder for AIRPORT_LIST. Keep minimal to avoid
pulling large datasets into the image during deployment. If you need actual
airport metadata later, swap in `airportsdata` usage or a curated JSON file.
"""

# Minimal mapping {"IATA_OR_ICAO_CODE": { ... }} used by outlines if referenced.
AIRPORT_LIST = {}
