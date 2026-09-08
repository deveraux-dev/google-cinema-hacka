import pytest
from engine.db import log_run, get_latest_run

def test_db_log_and_retrieve():
    sample_output = {
        "project": "Universal CallSheet",
        "scene": {"id": "TEST_S1", "heading": "TEST SCENE"},
        "safety": {"severity": "RED", "required_clears": ["Safety officer clear"]},
        "hazard_tags": [{"row": 2, "label": "pyro"}]
    }
    
    log_run(sample_output)
    latest = get_latest_run()
    
    assert latest is not None
    assert latest["scene"]["id"] == "TEST_S1"
    assert latest["safety"]["severity"] == "RED"
