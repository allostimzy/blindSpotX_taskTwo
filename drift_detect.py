from db import get_snapshots
from deepdiff import DeepDiff
import json

def detect_drift():
    snapshots = get_snapshots()
    if len(snapshots) < 2:
        print("Not enough snapshots to detect drift.")
        return {}

    # Compare the two most recent snapshots
    latest = snapshots[0]
    previous = snapshots[1]

    diff = DeepDiff(previous, latest, ignore_order=True)

    if diff:
        print("Drift detected between the two most recent snapshots:")
        diff_report = json.dumps(diff, indent=4)
        print(diff_report)
        return diff
    else:
        print("No drift detected.")
        return {}

if __name__ == "__main__":
    detect_drift()
