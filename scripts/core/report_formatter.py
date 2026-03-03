#!/usr/bin/env python3
"""
Report Formatter for Sales Strategy Reporting Agent
Handles formatting of data for different output types
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReportFormatter:
    """Format report data for various output types"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize formatter with configuration

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.formatting = self.config.get('formatting', {})

    def to_dataframe(
        self,
        data: List[Dict[str, Any]],
        rename_columns: bool = True
    ) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame

        Args:
            data: List of dictionaries
            rename_columns: Whether to prettify column names

        Returns:
            DataFrame
        """
        if not data:
            logger.warning("No data to convert to DataFrame")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        if rename_columns:
            # Convert SNAKE_CASE to Title Case
            df.columns = [
                col.replace('_', ' ').title()
                for col in df.columns
            ]

        return df

    def format_slack_message(
        self,
        data: List[Dict[str, Any]],
        title: str,
        subtitle: Optional[str] = None,
        include_summary: bool = True,
        emoji: str = "📊"
    ) -> str:
        """
        Format data as Slack markdown message

        Args:
            data: Report data
            title: Report title
            subtitle: Optional subtitle
            include_summary: Include summary section
            emoji: Emoji for title

        Returns:
            Formatted Slack message
        """
        if not data:
            return f"{emoji} *{title}*\n_No data available_"

        message = f"{emoji} *{title}*\n"

        if subtitle:
            message += f"_{subtitle}_\n"

        message += "\n"

        # Add summary if requested
        if include_summary:
            message += self._generate_summary(data)
            message += "\n"

        # Add detailed breakdown
        message += "*Breakdown:*\n"
        for row in data:
            message += self._format_row_slack(row)
            message += "\n"

        # Footer
        message += f"\n_Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}_"

        return message

    def _generate_summary(self, data: List[Dict[str, Any]]) -> str:
        """Generate summary section for reports"""
        # This is report-specific and should be overridden
        # For now, return generic stats
        return f"*Summary:*\n• Total Records: {len(data)}\n"

    def _format_row_slack(self, row: Dict[str, Any]) -> str:
        """Format a single row for Slack"""
        # Basic formatting - can be customized per report
        formatted = "\n*"

        # Find primary key (usually first field or 'leader'/'segment')
        primary_key = None
        for key in ['LEADER', 'SEGMENT', 'REGION', 'NAME']:
            if key in row:
                primary_key = key
                break

        if not primary_key:
            primary_key = list(row.keys())[0]

        formatted += f"{row[primary_key]}*\n"

        # Format other fields
        for key, value in row.items():
            if key != primary_key:
                label = key.replace('_', ' ').title()

                # Format based on type
                if isinstance(value, float):
                    if 'PCT' in key or 'PERCENT' in key:
                        formatted += f"  • {label}: {value}%\n"
                    else:
                        formatted += f"  • {label}: {value:,.2f}\n"
                elif isinstance(value, int):
                    formatted += f"  • {label}: {value:,}\n"
                else:
                    formatted += f"  • {label}: {value}\n"

        return formatted

    def save_csv(
        self,
        data: List[Dict[str, Any]],
        filepath: str,
        include_index: bool = False
    ) -> bool:
        """
        Save data as CSV

        Args:
            data: Report data
            filepath: Output file path
            include_index: Include DataFrame index

        Returns:
            True if successful
        """
        try:
            df = self.to_dataframe(data)
            df.to_csv(filepath, index=include_index)
            logger.info(f"Saved CSV to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
            return False

    def save_excel(
        self,
        data: List[Dict[str, Any]],
        filepath: str,
        sheet_name: str = "Report",
        auto_width: bool = True,
        freeze_panes: Optional[tuple] = (1, 0)
    ) -> bool:
        """
        Save data as formatted Excel file

        Args:
            data: Report data
            filepath: Output file path
            sheet_name: Name of the worksheet
            auto_width: Auto-adjust column widths
            freeze_panes: Row/column to freeze (row, col)

        Returns:
            True if successful
        """
        try:
            df = self.to_dataframe(data)

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                worksheet = writer.sheets[sheet_name]

                # Auto-adjust column widths
                if auto_width:
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).map(len).max(),
                            len(col)
                        ) + 2
                        col_letter = chr(65 + idx)
                        worksheet.column_dimensions[col_letter].width = max_length

                # Freeze panes
                if freeze_panes:
                    cell = f"{chr(65 + freeze_panes[1])}{freeze_panes[0] + 1}"
                    worksheet.freeze_panes = cell

            logger.info(f"Saved Excel to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save Excel: {e}")
            return False

    def format_number(self, value: float, format_type: str = 'number') -> str:
        """
        Format a number according to configuration

        Args:
            value: Number to format
            format_type: Type (number, percentage, currency)

        Returns:
            Formatted string
        """
        if format_type == 'percentage':
            decimal_places = self.formatting.get('percentage_format', {}).get('decimal_places', 2)
            return f"{value:.{decimal_places}f}%"

        elif format_type == 'currency':
            return f"${value:,.2f}"

        else:  # number
            decimal_places = self.formatting.get('number_format', {}).get('decimal_places', 2)
            return f"{value:,.{decimal_places}f}"
