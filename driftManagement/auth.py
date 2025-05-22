import os
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv

load_dotenv()

# Load environment variables from .env file
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

# Check if environment variables are set
def get_credentials():
    return ClientSecretCredential(
        tenant_id="TENANT_ID",
        client_id="CLIENT_ID",
        client_secret="CLIENT_SECRET",
        subscription_id = "SUBSCRIPTION_ID"
    )

# Get the credentials for Azure
def get_graph_token():
    """
    Get access token for Microsoft Graph API.
    """
    credential = get_credentials()
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token
