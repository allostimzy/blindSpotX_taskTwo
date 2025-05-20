from flask import Flask, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from poll_azure import collect_snapshot
from ingest import ingest_signin_logs
from db import get_snapshots, get_signin_logs
from drift_detect import detect_drift
from datetime import datetime

app = Flask(__name__)

# Schedule snapshot collection every 30 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(func=collect_snapshot, trigger="interval", minutes=30)
scheduler.add_job(func=ingest_signin_logs, trigger="interval", minutes=10)
scheduler.start()

@app.route("/")
def index():
    snapshots = get_snapshots()
    drift = detect_drift()
    return render_template("index.html", snapshots=snapshots, drift=drift, current_year=datetime.now().year)

@app.route("/snapshots", methods=["GET"])
def snapshots():
    return jsonify(get_snapshots())

@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(get_signin_logs())

@app.route("/drift", methods=["GET"])
def drift():
    return jsonify(detect_drift())

if __name__ == "__main__":
    app.run(debug=True)
