import requests
from auth import get_graph_token
from db import save_signin_logs

GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/auditLogs/signIns"

def ingest_signin_logs():
    token = get_graph_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    logs = []
    url = GRAPH_ENDPOINT

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch logs: {response.status_code} {response.text}")
            break

        data = response.json()
        logs.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Handle pagination

    if logs:
        save_signin_logs(logs)
        print(f"{len(logs)} sign-in logs ingested.")
    else:
        print("No new sign-in logs found.")

if __name__ == "__main__":
    ingest_signin_logs()
