# import requests
#
# # Replace these with your actual values
# client_id = '1994f9dd-edb1-4695-9d2b-dc0a4445b7ec'
# client_secret = 'e353926e-29fd-4792-aa01-ed4f38797db5'
# tenant_id = '8b49d279-a78b-4b20-bc06-53bcae801d5b'
#
# # URL to get the token
# token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
#
# # Prepare the token request payload
# token_data = {
#     'grant_type': 'client_credentials',
#     'client_id': client_id,
#     'client_secret': client_secret,
#     'scope': 'https://graph.microsoft.com/.default'
# }
#
# # Request the token
# token_r = requests.post(token_url, data=token_data)
# token_r.raise_for_status()
# token = token_r.json().get('access_token')

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

# Replace these with your actual values
client_id = '1994f9dd-edb1-4695-9d2b-dc0a4445b7ec'
client_secret = 'e353926e-29fd-4792-aa01-ed4f38797db5'
tenant_id = '8b49d279-a78b-4b20-bc06-53bcae801d5b'
site_url = 'https://apagcosyst0.sharepoint.com/sites/ProgramDMS'

# Create client credentials
credentials = ClientCredential(client_id, client_secret)

# Authenticate and create the client context
ctx = ClientContext(site_url).with_credentials(credentials)

# Load the target document library
doc_lib_title = '/production/WorkInstructions'  # Replace with your document library name
doc_lib = ctx.web.lists.get_by_title(doc_lib_title)
ctx.load(doc_lib)
ctx.execute_query()

# List files in the document library
files = doc_lib.root_folder.files
ctx.load(files)
ctx.execute_query()

# Print the details of each file
for file in files:
    print(f"Name: {file.properties['Name']}, URL: {file.properties['ServerRelativeUrl']}")
