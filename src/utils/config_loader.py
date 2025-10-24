"""
Configuration Loader Utility
Loads YAML configurations and manages secrets
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

class ConfigLoader:
    """Loads and manages configuration from YAML files"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config loader

        Args:
            config_dir: Directory containing config files (default: configs/)
        """
        if config_dir is None:
            config_dir = Path('configs')

        self.config_dir = Path(config_dir)
        self._config_cache: Dict[str, Dict] = {}

    def load_config(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Args:
            config_name: Name of config file (without .yaml extension)
            use_cache: Use cached config if available

        Returns:
            Dict with configuration data

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        # Check cache
        if use_cache and config_name in self._config_cache:
            logger.debug(f"Loading {config_name} from cache")
            return self._config_cache[config_name]

        # Build file path
        config_file = self.config_dir / f"{config_name}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Load YAML
        logger.debug(f"Loading config from {config_file}")

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Substitute environment variables
            config = self._substitute_env_vars(config)

            # Cache config
            if use_cache:
                self._config_cache[config_name] = config

            logger.info(f"Successfully loaded config: {config_name}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {config_file}: {e}")
            raise

        except Exception as e:
            logger.error(f"Failed to load config {config_name}: {e}")
            raise

    def _substitute_env_vars(self, config: Any) -> Any:
        """
        Recursively substitute environment variables in config

        Supports syntax: ${VAR_NAME:default_value}

        Args:
            config: Configuration dict/list/str

        Returns:
            Configuration with env vars substituted
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}

        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]

        elif isinstance(config, str):
            # Check for env var syntax: ${VAR:default}
            if config.startswith('${') and config.endswith('}'):
                var_spec = config[2:-1]

                # Parse variable name and default
                if ':' in var_spec:
                    var_name, default = var_spec.split(':', 1)
                else:
                    var_name, default = var_spec, ''

                # Get from environment
                return os.getenv(var_name, default)

            return config

        else:
            return config

    def get_nested(self, config: Dict, path: str, default: Any = None) -> Any:
        """
        Get nested configuration value using dot notation

        Args:
            config: Configuration dict
            path: Dot-separated path (e.g., 'trading.bots.dee_bot.enabled')
            default: Default value if path doesn't exist

        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        value = config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def validate_config(self, config: Dict, required_keys: list) -> tuple[bool, list]:
        """
        Validate that required keys exist in config

        Args:
            config: Configuration dict
            required_keys: List of required keys (supports dot notation)

        Returns:
            Tuple of (is_valid, missing_keys)
        """
        missing_keys = []

        for key in required_keys:
            value = self.get_nested(config, key)
            if value is None:
                missing_keys.append(key)

        is_valid = len(missing_keys) == 0

        if not is_valid:
            logger.warning(f"Missing required config keys: {missing_keys}")

        return is_valid, missing_keys


# ============================================================================
# SECRETS MANAGEMENT
# ============================================================================

def get_secret(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Retrieve secret/API key from environment variables

    Args:
        key: Environment variable name
        default: Default value if not found
        required: Raise error if not found and no default

    Returns:
        Secret value or default

    Raises:
        ValueError: If required=True and secret not found
    """
    value = os.getenv(key, default)

    if value is None and required:
        raise ValueError(f"Required secret '{key}' not found in environment variables")

    if value:
        logger.debug(f"Retrieved secret: {key}")
    else:
        logger.warning(f"Secret '{key}' not found, using default")

    return value


def load_env_file(env_file: Optional[Path] = None):
    """
    Load environment variables from .env file

    Args:
        env_file: Path to .env file (default: configs/.env)
    """
    if env_file is None:
        env_file = Path('configs/.env')

    if not env_file.exists():
        logger.warning(f".env file not found: {env_file}")
        return

    logger.info(f"Loading environment from {env_file}")

    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Set environment variable (don't override existing)
                if key not in os.environ:
                    os.environ[key] = value


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global config loader instance
_config_loader = None


def get_config_loader(config_dir: Optional[Path] = None) -> ConfigLoader:
    """Get singleton config loader instance"""
    global _config_loader

    if _config_loader is None:
        _config_loader = ConfigLoader(config_dir)

    return _config_loader


def load_config(config_name: str, config_dir: Optional[Path] = None) -> Dict:
    """
    Load configuration file

    Args:
        config_name: Name of config file (without .yaml)
        config_dir: Config directory (default: configs/)

    Returns:
        Dict with configuration
    """
    loader = get_config_loader(config_dir)
    return loader.load_config(config_name)


def validate_config(config: Dict, required_keys: list) -> tuple[bool, list]:
    """
    Validate configuration has required keys

    Args:
        config: Configuration dict
        required_keys: List of required keys

    Returns:
        Tuple of (is_valid, missing_keys)
    """
    loader = get_config_loader()
    return loader.validate_config(config, required_keys)


# Example usage
if __name__ == '__main__':
    # Load environment
    load_env_file()

    # Load configurations
    config = load_config('config')
    print("Main config loaded:", config.keys())

    data_sources = load_config('data_sources')
    print("Data sources loaded:", len(data_sources))

    # Get nested value
    loader = get_config_loader()
    enabled = loader.get_nested(config, 'feature_flags.multi_agent_system', default=False)
    print(f"Multi-agent system enabled: {enabled}")

    # Validate config
    required = ['environment', 'trading.mode', 'feature_flags']
    is_valid, missing = validate_config(config, required)
    print(f"Config valid: {is_valid}, Missing: {missing}")

    # Get secrets
    api_key = get_secret('ANTHROPIC_API_KEY', required=False)
    print(f"API key found: {api_key is not None}")
