import tvheadend.tvh as TVH

def test_getFinishedRecordings():
    total, entries = TVH.finishedRecordings("chris", "internal")
    assert len(entries) == total
