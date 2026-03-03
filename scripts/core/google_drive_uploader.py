#!/usr/bin/env python3
"""
Google Drive Uploader for Sales Strategy Reporting Agent
Handles authentication and file uploads to Google Drive
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json
# NOTE: 'drive' scope (not 'drive.file') is required for shared drive access
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]


class GoogleDriveUploader:
    """Handles Google Drive file operations"""

    def __init__(self, credentials_path='config/google_credentials.json', shared_drive_name=None):
        """
        Initialize the uploader with credentials

        Args:
            credentials_path: Path to OAuth credentials file
            shared_drive_name: Name of shared drive (Team Drive) to use, or None for personal drive
        """
        self.credentials_path = credentials_path
        self.token_path = 'config/token.json'
        self.creds = None
        self.service = None
        self.shared_drive_id = None
        self.shared_drive_name = shared_drive_name
        self._authenticate()

        # Look up shared drive if name provided
        if self.shared_drive_name:
            self.shared_drive_id = self.get_shared_drive_id(self.shared_drive_name)
            if self.shared_drive_id:
                print(f"✅ Connected to shared drive: {self.shared_drive_name}")

    def _authenticate(self):
        """Authenticate with Google Drive API"""
        # Check if we have saved credentials
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If credentials are invalid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}\n"
                        "Please download OAuth 2.0 credentials from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        # Build the service
        self.service = build('drive', 'v3', credentials=self.creds)
        print("✅ Successfully authenticated with Google Drive")

    def get_shared_drive_id(self, drive_name):
        """
        Find shared drive (Team Drive) by name

        Args:
            drive_name: Name of the shared drive to find

        Returns:
            Drive ID if found, None otherwise
        """
        try:
            # List all shared drives accessible to the user
            results = self.service.drives().list(
                pageSize=100,
                fields="drives(id, name)"
            ).execute()

            drives = results.get('drives', [])

            for drive in drives:
                if drive['name'] == drive_name:
                    print(f"📁 Found shared drive: {drive_name} (ID: {drive['id']})")
                    return drive['id']

            print(f"⚠️  Shared drive '{drive_name}' not found")
            print(f"   Available drives: {', '.join([d['name'] for d in drives]) or 'None'}")
            return None

        except HttpError as error:
            print(f"❌ Error finding shared drive: {error}")
            return None

    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            # Add shared drive support if configured
            create_params = {
                'body': file_metadata,
                'fields': 'id, name',
                'supportsAllDrives': True
            }

            folder = self.service.files().create(**create_params).execute()

            print(f"✅ Created folder: {folder.get('name')} (ID: {folder.get('id')})")
            return folder.get('id')

        except HttpError as error:
            print(f"❌ Error creating folder: {error}")
            return None

    def upload_file(self, file_path, folder_id=None, mime_type=None):
        """Upload a file to Google Drive"""
        try:
            file_name = Path(file_path).name

            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Determine mime type if not provided
            if mime_type is None:
                ext = Path(file_path).suffix.lower()
                mime_types = {
                    '.csv': 'text/csv',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.pdf': 'application/pdf',
                    '.json': 'application/json',
                    '.txt': 'text/plain'
                }
                mime_type = mime_types.get(ext, 'application/octet-stream')

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            # Add shared drive support if configured
            create_params = {
                'body': file_metadata,
                'media_body': media,
                'fields': 'id, name, webViewLink',
                'supportsAllDrives': True
            }

            file = self.service.files().create(**create_params).execute()

            print(f"✅ Uploaded: {file.get('name')}")
            print(f"   Link: {file.get('webViewLink')}")

            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'link': file.get('webViewLink')
            }

        except HttpError as error:
            print(f"❌ Error uploading file: {error}")
            return None

    def list_files(self, folder_id=None, page_size=10):
        """List files in Google Drive"""
        try:
            query = []
            if folder_id:
                query.append(f"'{folder_id}' in parents")

            # Build list parameters with shared drive support
            list_params = {
                'q': ' and '.join(query) if query else None,
                'pageSize': page_size,
                'fields': "nextPageToken, files(id, name, mimeType, createdTime, webViewLink)",
                'supportsAllDrives': True,
                'includeItemsFromAllDrives': True
            }

            results = self.service.files().list(**list_params).execute()

            items = results.get('files', [])

            if not items:
                print('No files found.')
                return []

            print('Files:')
            for item in items:
                print(f"  {item['name']} ({item['id']})")

            return items

        except HttpError as error:
            print(f"❌ Error listing files: {error}")
            return []

    def get_folder_id(self, folder_name, create_if_not_exists=True):
        """
        Get folder ID by name, optionally creating if it doesn't exist

        Args:
            folder_name: Name of the folder to find
            create_if_not_exists: Create folder if not found

        Returns:
            Folder ID if found/created, None otherwise
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"

            # Build list parameters
            list_params = {
                'q': query,
                'spaces': 'drive',
                'fields': 'files(id, name)',
                'supportsAllDrives': True,
                'includeItemsFromAllDrives': True
            }

            # If searching within a shared drive, specify it
            if self.shared_drive_id:
                list_params['driveId'] = self.shared_drive_id
                list_params['corpora'] = 'drive'  # Search within specific drive

            results = self.service.files().list(**list_params).execute()

            items = results.get('files', [])

            if items:
                folder_id = items[0]['id']
                drive_context = f" in shared drive '{self.shared_drive_name}'" if self.shared_drive_id else ""
                print(f"📁 Found folder: {folder_name}{drive_context} (ID: {folder_id})")
                return folder_id
            elif create_if_not_exists:
                drive_context = f" in shared drive '{self.shared_drive_name}'" if self.shared_drive_id else ""
                print(f"📁 Folder '{folder_name}' not found{drive_context}. Creating...")
                # Note: When creating in shared drive, must specify parent as shared drive root
                # This is handled by passing parent_folder_id to create_folder
                return self.create_folder(folder_name)
            else:
                print(f"📁 Folder '{folder_name}' not found.")
                return None

        except HttpError as error:
            print(f"❌ Error finding folder: {error}")
            return None


def main():
    """Test the Google Drive uploader"""
    uploader = GoogleDriveUploader()

    # Get or create the Zendesk AI Reports folder
    folder_id = uploader.get_folder_id("Zendesk AI Reports", create_if_not_exists=True)

    if folder_id:
        print(f"\n✅ Ready to upload files to folder ID: {folder_id}")
        print("\nTo upload a file, use:")
        print(f"  uploader.upload_file('path/to/file.csv', folder_id='{folder_id}')")


if __name__ == '__main__':
    main()
