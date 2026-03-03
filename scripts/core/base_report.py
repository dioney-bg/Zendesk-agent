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

    def run(self, formats: List[str] = None) -> Dict[str, Any]:
        """
        Run the complete report pipeline

        Args:
            formats: List of output formats (csv, excel, slack)

        Returns:
            Dictionary of generated outputs
        """
        if formats is None:
            # Get default formats from config
            report_info = self.config.get('reports', {}).get(self.report_code, {})
            formats = report_info.get('outputs', ['csv', 'excel'])

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

        if 'excel' in formats:
            excel_path = self.save_excel(data)
            if excel_path:
                results['excel'] = excel_path
                logger.info(f"✅ Excel: {excel_path}")

        if 'slack' in formats:
            slack_msg = self.format_slack(data)
            results['slack'] = slack_msg
            logger.info("✅ Slack message formatted")

        return results
