#!/usr/bin/env python3
"""
Base Report Class for Sales Strategy Reporting Agent
All specific reports inherit from this class
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from .snowflake_client import SnowflakeClient
from .report_formatter import ReportFormatter

try:
    from .google_drive_uploader import GoogleDriveUploader
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseReport(ABC):
    """
    Abstract base class for all reports

    Each specific report should inherit from this and implement:
    - generate_query(): Return the SQL query
    - process_data(): Transform raw data if needed
    """

    def __init__(
        self,
        report_code: str,
        config_path: str = 'config/config.yaml'
    ):
        """
        Initialize report

        Args:
            report_code: Unique code for this report
            config_path: Path to main configuration file
        """
        self.report_code = report_code
        self.config = self._load_config(config_path)
        self.report_config = self._load_report_config()

        # Initialize clients
        sf_config = self.config.get('snowflake', {})
        self.snowflake = SnowflakeClient(
            connection_name=sf_config.get('connection_name')
        )
        self.formatter = ReportFormatter(self.config)

        # Initialize Google Drive uploader if enabled
        self.drive_uploader = None
        drive_config = self.config.get('google_drive', {})
        if drive_config.get('enabled', False) and GOOGLE_DRIVE_AVAILABLE:
            try:
                # Check if using shared drive
                if drive_config.get('use_shared_drive', False):
                    shared_drive_name = drive_config.get('shared_drive_name')
                    self.drive_uploader = GoogleDriveUploader(
                        shared_drive_name=shared_drive_name
                    )
                else:
                    # Personal drive mode
                    self.drive_uploader = GoogleDriveUploader()

                logger.info("Google Drive uploader initialized")
            except FileNotFoundError:
                logger.warning("Google Drive credentials not found. Uploads disabled.")
            except Exception as e:
                logger.warning(f"Could not initialize Google Drive: {e}")

        logger.info(f"Initialized report: {self.report_code}")

    def _load_config(self, config_path: str) -> Dict:
        """Load main configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_report_config(self) -> Dict:
        """Load report-specific configuration"""
        report_info = self.config.get('reports', {}).get(self.report_code, {})
        config_file = report_info.get('config_file')

        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)

        return {}

    @abstractmethod
    def generate_query(self) -> str:
        """
        Generate the SQL query for this report

        Returns:
            SQL query string
        """
        pass

    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process/transform raw data

        Args:
            data: Raw data from query

        Returns:
            Processed data

        Note: Override this method if you need to transform data
        """
        return data

    def execute(self) -> Optional[List[Dict[str, Any]]]:
        """
        Execute the report query

        Returns:
            Query results
        """
        logger.info(f"Executing report: {self.report_code}")

        query = self.generate_query()
        data = self.snowflake.execute_query(query)

        if data:
            data = self.process_data(data)
            logger.info(f"Report returned {len(data)} rows")
            return data

        logger.error("Report execution failed")
        return None

    def save_csv(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Save report as CSV

        Args:
            data: Report data
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.report_code}_{timestamp}.csv"

        # Organize by report type
        output_config = self.config.get('output', {})
        if output_config.get('organize_by_report', True):
            output_dir = Path(output_config['reports_dir']) / self.report_code
        else:
            output_dir = Path(output_config['reports_dir'])

        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename

        if self.formatter.save_csv(data, str(filepath)):
            return str(filepath)

        return None

    def save_excel(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Save report as Excel

        Args:
            data: Report data
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.report_code}_{timestamp}.xlsx"

        # Organize by report type
        output_config = self.config.get('output', {})
        if output_config.get('organize_by_report', True):
            output_dir = Path(output_config['reports_dir']) / self.report_code
        else:
            output_dir = Path(output_config['reports_dir'])

        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename

        # Get report-specific Excel config
        report_output = self.report_config.get('output', {}).get('excel', {})
        sheet_name = report_output.get('sheet_name', 'Report')

        if self.formatter.save_excel(data, str(filepath), sheet_name=sheet_name):
            return str(filepath)

        return None

    def format_slack(self, data: List[Dict[str, Any]]) -> str:
        """
        Format report for Slack

        Args:
            data: Report data

        Returns:
            Slack-formatted message
        """
        report_info = self.report_config.get('report', {})
        output_config = self.report_config.get('output', {}).get('slack', {})

        title = report_info.get('name', self.report_code)
        subtitle = report_info.get('description')
        emoji = output_config.get('emoji', '📊')

        return self.formatter.format_slack_message(
            data,
            title=title,
            subtitle=subtitle,
            emoji=emoji
        )

    def upload_to_drive(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to Google Drive

        Args:
            file_path: Path to file to upload

        Returns:
            Upload result dict with 'id', 'name', 'link' or None if failed
        """
        if not self.drive_uploader:
            logger.warning("Google Drive uploader not initialized")
            return None

        try:
            drive_config = self.config.get('google_drive', {})

            # Determine target folder
            if drive_config.get('use_shared_drive', False):
                # Shared drive mode - use target folder
                folder_name = drive_config.get('target_folder_name', 'Strategy-agent')

                # Optionally create subfolder by report type
                if drive_config.get('folder_structure', {}).get('by_report', False):
                    # Get main folder first
                    main_folder_id = self.drive_uploader.get_folder_id(
                        folder_name,
                        create_if_not_exists=True
                    )

                    if main_folder_id:
                        # Create report-specific subfolder
                        report_folder_name = self.report_code
                        # Search for subfolder within main folder
                        # Note: This requires additional logic to search within a parent
                        # For now, we'll just use the main folder
                        folder_id = main_folder_id
                    else:
                        logger.error(f"Could not create folder: {folder_name}")
                        return None
                else:
                    folder_id = self.drive_uploader.get_folder_id(
                        folder_name,
                        create_if_not_exists=True
                    )
            else:
                # Personal drive mode - use root folder
                folder_name = drive_config.get('root_folder_name', 'Sales Strategy Reports')
                folder_id = self.drive_uploader.get_folder_id(
                    folder_name,
                    create_if_not_exists=True
                )

            if not folder_id:
                logger.error("Could not determine target folder")
                return None

            # Upload file
            result = self.drive_uploader.upload_file(file_path, folder_id=folder_id)

            if result:
                logger.info(f"✅ Uploaded to Google Drive: {result.get('link')}")

            return result

        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {e}")
            return None

    def run(self, formats: List[str] = None, upload_to_drive: bool = None) -> Dict[str, Any]:
        """
        Run the complete report pipeline

        Args:
            formats: List of output formats (csv, excel, slack)
            upload_to_drive: Whether to upload files to Google Drive (None = use config default)

        Returns:
            Dictionary of generated outputs
        """
        if formats is None:
            # Get default formats from config
            report_info = self.config.get('reports', {}).get(self.report_code, {})
            formats = report_info.get('outputs', ['csv', 'excel'])

        # Determine if we should upload to Drive
        if upload_to_drive is None:
            drive_config = self.config.get('google_drive', {})
            upload_to_drive = drive_config.get('enabled', False) and self.drive_uploader is not None

        logger.info(f"Running report '{self.report_code}' with formats: {formats}")

        # Execute query
        data = self.execute()
        if not data:
            logger.error("No data returned, aborting report generation")
            return {}

        results = {}

        # Generate outputs
        if 'csv' in formats:
            csv_path = self.save_csv(data)
            if csv_path:
                results['csv'] = csv_path
                logger.info(f"✅ CSV: {csv_path}")

                # Upload to Google Drive if enabled
                if upload_to_drive:
                    drive_result = self.upload_to_drive(csv_path)
                    if drive_result:
                        results['csv_drive_link'] = drive_result.get('link')

        if 'excel' in formats:
            excel_path = self.save_excel(data)
            if excel_path:
                results['excel'] = excel_path
                logger.info(f"✅ Excel: {excel_path}")

                # Upload to Google Drive if enabled
                if upload_to_drive:
                    drive_result = self.upload_to_drive(excel_path)
                    if drive_result:
                        results['excel_drive_link'] = drive_result.get('link')

        if 'slack' in formats:
            slack_msg = self.format_slack(data)
            results['slack'] = slack_msg
            logger.info("✅ Slack message formatted")

        return results
