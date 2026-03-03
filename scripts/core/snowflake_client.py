#!/usr/bin/env python3
"""
Snowflake Client for Sales Strategy Reporting Agent
Handles all Snowflake query execution via CLI
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SnowflakeClient:
    """Client for executing Snowflake queries via CLI"""

    def __init__(
        self,
        cli_path: str = '/Applications/SnowflakeCLI.app/Contents/MacOS/snow',
        connection_name: Optional[str] = None
    ):
        """
        Initialize Snowflake client

        Args:
            cli_path: Path to Snowflake CLI executable
            connection_name: Named connection (optional)
        """
        self.cli_path = cli_path
        self.connection_name = connection_name

        # Verify CLI exists
        if not Path(cli_path).exists():
            raise FileNotFoundError(f"Snowflake CLI not found at: {cli_path}")

        logger.info(f"Initialized Snowflake client with CLI: {cli_path}")

    def execute_query(
        self,
        query: str,
        format: str = 'json',
        timeout: int = 300
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query and return results

        Args:
            query: SQL query to execute
            format: Output format (json, csv, table)
            timeout: Query timeout in seconds

        Returns:
            List of result rows as dictionaries (for JSON format)
            or raw string (for other formats)
        """
        try:
            cmd = [self.cli_path, 'sql', '-q', query]

            if format:
                cmd.extend(['--format', format])

            if self.connection_name:
                cmd.extend(['-c', self.connection_name])

            logger.debug(f"Executing query: {query[:100]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )

            if format == 'json':
                if result.stdout.strip():
                    data = json.loads(result.stdout)
                    logger.info(f"Query returned {len(data)} rows")
                    return data
                else:
                    logger.warning("Query returned no data")
                    return []
            else:
                return result.stdout

        except subprocess.TimeoutExpired:
            logger.error(f"Query timeout after {timeout} seconds")
            return None

        except subprocess.CalledProcessError as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw output: {result.stdout[:500]}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return None

    def execute_query_from_file(
        self,
        file_path: str,
        **kwargs
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query from a file

        Args:
            file_path: Path to SQL file
            **kwargs: Additional arguments for execute_query

        Returns:
            Query results
        """
        try:
            with open(file_path, 'r') as f:
                query = f.read()

            logger.info(f"Executing query from file: {file_path}")
            return self.execute_query(query, **kwargs)

        except FileNotFoundError:
            logger.error(f"Query file not found: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error reading query file: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test the Snowflake connection

        Returns:
            True if connection is successful
        """
        try:
            result = self.execute_query("SELECT CURRENT_DATE() as today")
            if result and len(result) > 0:
                logger.info(f"Connection successful. Current date: {result[0].get('TODAY')}")
                return True
            else:
                logger.error("Connection test returned no results")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_table_info(
        self,
        table: str,
        schema: Optional[str] = None,
        database: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get information about a table's columns

        Args:
            table: Table name
            schema: Schema name (optional)
            database: Database name (optional)

        Returns:
            List of column information
        """
        full_table = table
        if schema:
            full_table = f"{schema}.{table}"
        if database:
            full_table = f"{database}.{full_table}"

        query = f"DESCRIBE TABLE {full_table}"

        return self.execute_query(query)

    def get_row_count(
        self,
        table: str,
        where_clause: Optional[str] = None
    ) -> Optional[int]:
        """
        Get row count for a table

        Args:
            table: Fully qualified table name
            where_clause: Optional WHERE clause

        Returns:
            Row count
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"

        result = self.execute_query(query)

        if result and len(result) > 0:
            return result[0].get('COUNT', 0)

        return None
