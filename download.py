from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from requests.exceptions import HTTPError
import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()

site_url = 'https://gimnazijabezigrad.sharepoint.com/'

username = os.getenv('SHAREPOINT_USERNAME')
password = os.getenv('SHAREPOINT_PASSWORD')

file_url_template = '/Nad/nadomeščanja_{date}.pdf'
local_path_template = 'substitutes_{date}.pdf'

def download_substitutes(date=None):
    if not date:
        date = datetime.now()
    date1 = date.strftime("%Y-%m-%d")
    date2 = date.strftime("%-d_%-"
    "m")
    local_path = local_path_template.format(date=date1)
    file_url = file_url_template.format(date=date2)

    ctx_auth = AuthenticationContext(site_url)
    if ctx_auth.acquire_token_for_user(username, password):
        ctx = ClientContext(site_url, ctx_auth)
        try:
            response = File.open_binary(ctx, file_url)
        except HTTPError:
            print(f"HTTP error. File not found: {file_url}")
            return
        with open(local_path, 'wb') as local_file:
            local_file.write(response.content)
    else:
        print(ctx_auth.get_last_error())

if __name__ == "__main__":
    download_substitutes(datetime(2025, 3, 18))