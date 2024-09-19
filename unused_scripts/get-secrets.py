import os
import requests
import vars


def get_hcp_api_token(client_id, client_secret):
    """
    Authenticate with HashiCorp Cloud and get an API token.
    """
    auth_url = "https://auth.hashicorp.com/oauth/token"
    auth_payload = {
        "audience": "https://api.hashicorp.cloud",
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(auth_url, json=auth_payload)
    response.raise_for_status()  # Ensure that the request was successful
    return response.json()["access_token"]


def get_secrets(api_token, secrets_url):
    """
    Retrieve secrets from HashiCorp Vault using the API token.
    """
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(secrets_url, headers=headers)
    response.raise_for_status()
    return response.json()


# Set Service Principal credentials (replace with your actual credentials)
os.environ["HCP_CLIENT_ID"] = vars.HCP_CLIENT_ID
os.environ["HCP_CLIENT_SECRET"] = vars.HCP_CLIENT_SECRET

# Get credentials from environment variables
client_id = os.getenv("HCP_CLIENT_ID")
client_secret = os.getenv("HCP_CLIENT_SECRET")

# Generate HCP API token
hcp_api_token = get_hcp_api_token(client_id, client_secret)

# Define the URL for your secrets (replace with your actual URL)
secrets_url = "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/bb0082bd-9809-41c7-93ae-3073ab5d4f53/projects/c349a31e-32a7-4f0a-beb0-6669a493ee92/apps/twitter/open"


# Function to parse secrets and get the value of a specific secret by its name
def get_specific_secret_value(secrets_response, secret_name):
    for secret in secrets_response["secrets"]:
        if secret["name"] == secret_name:
            # Return only the value of the secret
            return secret["version"]["value"]
    return None


# Example usage
all_secrets_response = get_secrets(hcp_api_token, secrets_url)
specific_secret_name = "BEARER_TOKEN"  # Replace with the name of the secret you want

# Get the value of the specific secret
specific_secret_value = get_specific_secret_value(
    all_secrets_response, specific_secret_name
)
if specific_secret_value:
    print(f"Value of Secret '{specific_secret_name}':", specific_secret_value)
else:
    print(f"Secret '{specific_secret_name}' not found")
