#!/usr/bin/env python3
"""
Test Shared Drive Connectivity
Verifies access to SalesStrategy shared drive and Strategy-agent folder
"""

import sys
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.google_drive_uploader import GoogleDriveUploader


def test_shared_drive():
    """Test shared drive connectivity"""

    # Load configuration
    config_path = Path('config/config.yaml')
    if not config_path.exists():
        print("❌ Configuration file not found: config/config.yaml")
        return False

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    drive_config = config.get('google_drive', {})

    # Check if Google Drive is enabled
    if not drive_config.get('enabled', False):
        print("⚠️  Google Drive is disabled in config/config.yaml")
        return False

    # Check if shared drive is configured
    use_shared_drive = drive_config.get('use_shared_drive', False)
    if not use_shared_drive:
        print("⚠️  Shared drive mode is disabled in config/config.yaml")
        print("   Set google_drive.use_shared_drive: true to enable")
        return False

    shared_drive_name = drive_config.get('shared_drive_name')
    target_folder_name = drive_config.get('target_folder_name')

    if not shared_drive_name:
        print("❌ Shared drive name not configured in config/config.yaml")
        return False

    print(f"📁 Testing connection to shared drive: {shared_drive_name}")
    print(f"📂 Target folder: {target_folder_name}")
    print()

    try:
        # Initialize uploader with shared drive
        uploader = GoogleDriveUploader(shared_drive_name=shared_drive_name)

        # Check if shared drive was found
        if not uploader.shared_drive_id:
            print(f"❌ Could not find shared drive: {shared_drive_name}")
            print()
            print("Possible issues:")
            print("  • You don't have access to the shared drive")
            print("  • The shared drive name is incorrect")
            print("  • Your OAuth token needs to be refreshed")
            print()
            print("Solutions:")
            print("  • Ask admin to add you to the shared drive")
            print("  • Check drive name in config/config.yaml")
            print("  • Delete config/token.json and re-authenticate")
            return False

        print(f"✅ Connected to shared drive: {shared_drive_name}")
        print(f"   Drive ID: {uploader.shared_drive_id}")
        print()

        # Test finding target folder
        if target_folder_name:
            print(f"🔍 Looking for folder: {target_folder_name}")
            folder_id = uploader.get_folder_id(
                target_folder_name,
                create_if_not_exists=False
            )

            if folder_id:
                print(f"✅ Found target folder: {target_folder_name}")
                print(f"   Folder ID: {folder_id}")
            else:
                print(f"⚠️  Target folder '{target_folder_name}' not found")
                print("   The folder will be created automatically on first upload")

        print()
        print("✅ Shared drive connectivity test PASSED")
        return True

    except FileNotFoundError as e:
        print("❌ Google Drive credentials not found")
        print()
        print("Please run: make setup-drive")
        print("Or see: docs/GOOGLE_DRIVE_SETUP.md")
        return False

    except Exception as e:
        print(f"❌ Error testing shared drive: {e}")
        print()
        print("Troubleshooting:")
        print("  • Check your internet connection")
        print("  • Verify OAuth token: delete config/token.json and re-authenticate")
        print("  • Run: make setup-drive")
        return False


def main():
    """Main entry point"""
    print("═" * 70)
    print("  🔍 Shared Drive Connectivity Test")
    print("═" * 70)
    print()

    success = test_shared_drive()

    print()
    print("═" * 70)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
