#!/usr/bin/env python3
"""
Report Pipeline - End-to-End Report Generation and Distribution
Generates reports and uploads to Google Drive
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_ai_report import AIReportGenerator
from scripts.google_drive_uploader import GoogleDriveUploader


def run_pipeline(upload_to_drive=True, formats=None):
    """Run the complete report pipeline"""
    if formats is None:
        formats = ['csv', 'excel', 'slack']

    print("=" * 80)
    print("ZENDESK AI REPORTS - AUTOMATED PIPELINE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Generate reports
    print("STEP 1: Generating Reports")
    print("-" * 80)
    generator = AIReportGenerator()
    results = generator.generate_report(formats=formats)

    if not results:
        print("❌ Pipeline failed: Could not generate reports")
        return False

    print()

    # Step 2: Upload to Google Drive (if enabled)
    if upload_to_drive and ('csv' in results or 'excel' in results):
        print("STEP 2: Uploading to Google Drive")
        print("-" * 80)

        try:
            uploader = GoogleDriveUploader()
            folder_id = uploader.get_folder_id("Zendesk AI Reports", create_if_not_exists=True)

            if folder_id:
                uploaded_files = []

                # Upload CSV
                if 'csv' in results:
                    print("\n📤 Uploading CSV...")
                    result = uploader.upload_file(results['csv'], folder_id=folder_id)
                    if result:
                        uploaded_files.append(result)

                # Upload Excel
                if 'excel' in results:
                    print("\n📤 Uploading Excel...")
                    result = uploader.upload_file(results['excel'], folder_id=folder_id)
                    if result:
                        uploaded_files.append(result)

                print()
                print("=" * 80)
                print("✅ PIPELINE COMPLETE")
                print("=" * 80)
                print(f"\n📊 Generated {len(results)} report(s)")
                print(f"☁️  Uploaded {len(uploaded_files)} file(s) to Google Drive")

                if uploaded_files:
                    print("\n🔗 Google Drive Links:")
                    for file in uploaded_files:
                        print(f"   • {file['name']}: {file['link']}")

                if 'slack' in results:
                    print("\n📋 Slack message copied to clipboard - paste in any channel!")

            else:
                print("⚠️  Could not find or create Google Drive folder")
                print("   Reports were generated locally")

        except FileNotFoundError as e:
            print(f"\n⚠️  Google Drive upload skipped: {e}")
            print("   To enable, set up Google credentials following README.md")
            print("   Reports were generated locally")
        except Exception as e:
            print(f"\n⚠️  Google Drive upload failed: {e}")
            print("   Reports were generated locally")

    else:
        print()
        print("=" * 80)
        print("✅ PIPELINE COMPLETE (Drive upload disabled)")
        print("=" * 80)
        print(f"\n📊 Generated {len(results)} report(s)")

        if 'slack' in results:
            print("\n📋 Slack message copied to clipboard - paste in any channel!")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    return True


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Generate and distribute Zendesk AI penetration reports'
    )
    parser.add_argument(
        '--no-drive',
        action='store_true',
        help='Skip Google Drive upload'
    )
    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['csv', 'excel', 'slack'],
        default=['csv', 'excel', 'slack'],
        help='Report formats to generate'
    )

    args = parser.parse_args()

    success = run_pipeline(
        upload_to_drive=not args.no_drive,
        formats=args.formats
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
