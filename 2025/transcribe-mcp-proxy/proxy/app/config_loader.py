"""Configuration loader for S3/Environment Variables and Secrets Manager"""

import json
import os
import time
from typing import Dict, Optional, List
import logging

import boto3
from botocore.exceptions import ClientError

from .models import MCPConnector

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads configuration from S3 or environment variables and secrets from Secrets Manager"""

    def __init__(
        self,
        config_source: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
        config_refresh_interval: int = 300,
    ):
        """
        Initialize the config loader

        Args:
            config_source: Configuration source ('s3', 'env', or 'file', defaults to env var CONFIG_SOURCE or 's3')
            s3_bucket: S3 bucket name for config (defaults to env var S3_CONFIG_BUCKET)
            s3_key: S3 object key for config (defaults to env var S3_CONFIG_KEY)
            config_refresh_interval: How often to refresh config in seconds (defaults to env var or 300)
        """
        self.config_source = config_source or os.environ.get("CONFIG_SOURCE", "s3")
        self.s3_bucket = s3_bucket or os.environ.get("S3_CONFIG_BUCKET", "")
        self.s3_key = s3_key or os.environ.get("S3_CONFIG_KEY", "connectors.json")
        self.config_file = os.environ.get("MCP_CONFIG_FILE", "connectors.json")
        self.secrets_dir = os.environ.get("SECRETS_DIR", ".")
        self.config_refresh_interval = int(
            os.environ.get("CONFIG_REFRESH_INTERVAL", str(config_refresh_interval))
        )

        # Initialize AWS clients to None
        self.s3_client = None
        self.secretsmanager_client = None

        # Only initialize AWS clients if not using file-based config
        if self.config_source == "s3":
            self.s3_client = boto3.client("s3")
            self.secretsmanager_client = boto3.client("secretsmanager")
        elif self.config_source == "env":
            # env source might need Secrets Manager for secrets
            self.secretsmanager_client = boto3.client("secretsmanager")

        self._connectors: Dict[str, MCPConnector] = {}
        self._secrets_cache: Dict[str, tuple[str, float]] = {}
        self._config_last_loaded: float = 0
        self._config_version: int = 0

    def _get_configuration_from_s3(self) -> Optional[str]:
        """Get configuration from S3"""
        try:
            if not self.s3_bucket:
                raise ValueError(
                    "S3_CONFIG_BUCKET environment variable is required when CONFIG_SOURCE is 's3'"
                )

            logger.info(
                f"Fetching configuration from s3://{self.s3_bucket}/{self.s3_key}"
            )
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.s3_key)
            config_data = response["Body"].read()
            return config_data.decode("utf-8") if config_data else None

        except ClientError as e:
            logger.error(f"Failed to get S3 configuration: {e}")
            raise

    def _get_configuration_from_env(self) -> Optional[str]:
        """Get configuration from environment variable"""
        try:
            config_json = os.environ.get("CONNECTORS_JSON", "")
            if not config_json:
                raise ValueError(
                    "CONNECTORS_JSON environment variable is required when CONFIG_SOURCE is 'env'"
                )

            logger.info("Using configuration from CONNECTORS_JSON environment variable")
            return config_json

        except Exception as e:
            logger.error(f"Failed to get environment configuration: {e}")
            raise

    def _get_configuration_from_file(self) -> Optional[str]:
        """Get configuration from local file"""
        try:
            if not self.config_file:
                raise ValueError(
                    "MCP_CONFIG_FILE environment variable is required when CONFIG_SOURCE is 'file'"
                )

            logger.info(f"Loading configuration from local file: {self.config_file}")

            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = f.read()

            return config_data

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to read configuration file: {e}")
            raise

    def _get_latest_configuration(self) -> Optional[str]:
        """Get the latest configuration based on config source"""
        if self.config_source == "s3":
            return self._get_configuration_from_s3()
        elif self.config_source == "env":
            return self._get_configuration_from_env()
        elif self.config_source == "file":
            return self._get_configuration_from_file()
        else:
            raise ValueError(
                f"Unsupported CONFIG_SOURCE: {self.config_source}. Must be 's3', 'env', or 'file'"
            )

    def load_connectors(self, force_refresh: bool = False) -> Dict[str, MCPConnector]:
        """
        Load MCP connectors from S3, environment variables, or local file

        Args:
            force_refresh: Force refresh even if cache is still valid

        Returns:
            Dictionary of connector_id -> MCPConnector
        """
        current_time = time.time()

        # Check if we need to refresh
        if (
            not force_refresh
            and self._connectors
            and (current_time - self._config_last_loaded) < self.config_refresh_interval
        ):
            logger.debug("Using cached connector configuration")
            return self._connectors

        logger.info(f"Loading connector configuratioin from {self.config_source}")

        try:
            config_str = self._get_latest_configuration()

            if config_str:
                config_data = json.loads(config_str)
                connectors_list: List[dict] = config_data.get("connectors", [])

                new_connectors = {
                    connector_dict["id"]: MCPConnector(**connector_dict)
                    for connector_dict in connectors_list
                }

                # Check if configuration actually changed
                if new_connectors != self._connectors:
                    self._connectors = new_connectors
                    self._config_version += 1
                    logger.info(
                        f"Loaded {len(self._connectors)} connectors from {self.config_source} (version {self._config_version})"
                    )
                else:
                    logger.debug("Configuration unchanged")
            else:
                logger.debug(
                    f"No configuration data received from {self.config_source}"
                )

            # Always update the timestamp to respect the refresh interval
            self._config_last_loaded = current_time

            return self._connectors

        except Exception as e:
            logger.error(f"Failed to load connectors: {e}")
            # Return cached connectors if available
            if self._connectors:
                logger.warning("Returning cached connectors due to error")
                return self._connectors
            raise

    def get_connector(self, connector_id: str) -> Optional[MCPConnector]:
        """
        Get a specific connector by ID

        Args:
            connector_id: The connector ID to retrieve

        Returns:
            MCPConnector if found, None otherwise
        """
        # Ensure connectors are loaded
        if not self._connectors:
            self.load_connectors()

        return self._connectors.get(connector_id)

    def get_config_version(self) -> int:
        """
        Get the current configuration version

        Returns:
            Configuration version number (incremented on each change)
        """
        return self._config_version

    def get_secret(self, secret_arn: str, max_age: int = 300) -> Optional[str]:
        """
        Get a secret from Secrets Manager or local file with caching

        Args:
            secret_arn: ARN of the secret or file path (with file:// prefix for local files)
            max_age: Maximum age of cached secret in seconds (default 5 minutes)

        Returns:
            Secret string value or None if not found
        """
        current_time = time.time()

        # Check cache
        if secret_arn in self._secrets_cache:
            cached_value, cached_time = self._secrets_cache[secret_arn]
            if (current_time - cached_time) < max_age:
                logger.debug(f"Using cached secret for {secret_arn}")
                return cached_value

        # Check if this is a local file path (file:// prefix)
        if secret_arn.startswith("file://"):
            file_path = secret_arn[7:]

            # If relative path, resolve relative to secrets_dir
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.secrets_dir, file_path)

            try:
                logger.info(f"Loading secret from local file: {file_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    secret_value = f.read()

                # Cache the secret
                self._secrets_cache[secret_arn] = (secret_value, current_time)
                return secret_value

            except FileNotFoundError:
                logger.error(f"Secret file not found: {file_path}")
                raise
            except Exception as e:
                logger.error(f"Failed to read secret file {file_path}: {e}")
                raise

        # Fetch from Secrets Manager
        if not self.secretsmanager_client:
            raise ValueError(
                f"Secrets Manager not available for CONFIG_SOURCE={self.config_source}. Use file:// prefix for local secrets."
            )

        try:
            logger.info(f"Fetching secret from Secrets Manager: {secret_arn}")
            response = self.secretsmanager_client.get_secret_value(SecretId=secret_arn)

            secret_value = response.get("SecretString")
            if secret_value:
                # Cache the secret
                self._secrets_cache[secret_arn] = (secret_value, current_time)
                return secret_value

            return None

        except ClientError as e:
            logger.error(f"Failed to get secret {secret_arn}: {e}")
            # Return cached value if available, even if expired
            if secret_arn in self._secrets_cache:
                logger.warning(f"Returning expired cached secret for {secret_arn}")
                return self._secrets_cache[secret_arn][0]
            raise


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get the global config loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
