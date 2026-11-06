import os
import dropbox
from dropbox.exceptions import ApiError, AuthError
from dotenv import load_dotenv

load_dotenv()

class DropboxUploader:
    def __init__(self):
        self.access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        self.dbx = None
        self._authenticate()

    def _authenticate(self):
        if not self.access_token or self.access_token == "sl.your_generated_access_token_here":
            print(" Skipping Dropbox setup: Missing DROPBOX_ACCESS_TOKEN in .env")
            return

        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            self.dbx.users_get_current_account()
            print(" Connected to Dropbox Cloud Storage successfully.")
        except AuthError as e:
            print(f"❌ Dropbox Authentication failed: Invalid Access Token ({e})")
            self.dbx = None
        except Exception as e:
            print(f"❌ Could not connect to Dropbox: {e}")
            self.dbx = None

    def upload_file(self, local_file_path):
        if not self.dbx:
            print(" Skipping upload: Not authenticated with Dropbox.")
            return False

        if not os.path.exists(local_file_path):
            print(f" Skipping upload: File no longer exists ({local_file_path})")
            return False

        file_name = os.path.basename(local_file_path)
        dropbox_path = f"/{file_name}"

        try:
            print(f"☁️ Uploading '{file_name}' to Dropbox...")
            with open(local_file_path, "rb") as f:
                self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

            print(f" Dropbox upload complete: {file_name}")
            return True

        except ApiError as e:
            print(f"❌ Dropbox API Error uploading {file_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False