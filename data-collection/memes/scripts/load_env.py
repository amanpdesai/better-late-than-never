"""
Load environment variables from .env file
"""
import os
from pathlib import Path


def load_env():
    """Load environment variables from .env file in the memes directory."""
    # Look for .env file in parent directory (data-collection/memes/)
    env_file = Path(__file__).parent.parent / '.env'

    if not env_file.exists():
        print(f"Warning: .env file not found at {env_file}")
        print("Please create a .env file with your API credentials.")
        print("See .env.example for the required format.")
        return False

    # Read and parse .env file
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
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

                # Set environment variable
                os.environ[key] = value

    print(f"✓ Loaded environment variables from {env_file}")
    return True


if __name__ == '__main__':
    load_env()
