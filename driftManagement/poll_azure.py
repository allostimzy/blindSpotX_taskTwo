from datetime import datetime
import os
from dotenv import load_dotenv
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources import ResourceManagementClient as AzureResourcesClient
from auth import get_credentials
from db import save_snapshot

load_dotenv()

def collect_snapshot():
    credential = get_credentials()
    azureSub = os.getenv("AZURE_SUBSCRIPTION_ID")
    subscription_id = f"{azureSub}"

    rg_client = ResourceManagementClient(credential, subscription_id)
    res_client = AzureResourcesClient(credential, subscription_id)

    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "resources": []
    }

    # Fetch all resources once
    all_resources = list(res_client.resources.list())

    for rg in rg_client.resource_groups.list():
        rg_data = {
            "resource_group": rg.name,
            "location": rg.location,
            "resources": []
        }

        # Filter resources by current resource group
        rg_resources = [
            res for res in all_resources
            if res.id and rg.name and
            res.id.lower().split("/resourcegroups/")[1].split("/")[0] == rg.name.lower()
        ]

        for res in rg_resources:
            rg_data["resources"].append({
                "name": res.name,
                "type": res.type,
                "location": res.location,
                "id": res.id,
                "tags": res.tags
            })

        snapshot["resources"].append(rg_data)

    save_snapshot(snapshot)
    print("Snapshot collected and saved successfully.")

if __name__ == "__main__":
    collect_snapshot()
