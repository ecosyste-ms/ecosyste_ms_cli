"""Helper function to get API domain with proper precedence."""

import os
from typing import Optional


def get_domain_with_precedence(
    api_name: str, domain_override: Optional[str] = None, env_prefix: str = "ECOSYSTEMS"
) -> Optional[str]:
    """
    Get the API domain with proper precedence: --domain > ENV > default.

    Args:
        api_name: Name of the API (e.g., 'repos', 'packages')
        domain_override: Domain provided via --domain parameter
        env_prefix: Prefix for environment variables (default: 'ECOSYSTEMS')

    Returns:
        The domain to use, or None if default should be used

    Environment variables checked (in order):
    1. {ENV_PREFIX}_{API_NAME}_DOMAIN (e.g., ECOSYSTEMS_REPOS_DOMAIN)
    2. {ENV_PREFIX}_DOMAIN (e.g., ECOSYSTEMS_DOMAIN)
    """
    # First check --domain parameter if provided
    if domain_override:
        return domain_override

    # Then check API-specific environment variable
    api_specific_env = f"{env_prefix}_{api_name.upper()}_DOMAIN"
    api_specific_domain = os.environ.get(api_specific_env)
    if api_specific_domain:
        return api_specific_domain

    # Finally check general environment variable
    general_env = f"{env_prefix}_DOMAIN"
    general_domain = os.environ.get(general_env)
    if general_domain:
        return general_domain

    # Return None to use default
    return None


def build_base_url(domain: Optional[str], api_name: str) -> Optional[str]:
    """
    Build base URL from domain.

    Args:
        domain: The domain to use
        api_name: Name of the API (for potential subdomain construction)

    Returns:
        The base URL or None if no domain is provided
    """
    if not domain:
        return None

    # Reject plaintext HTTP — all traffic must use HTTPS
    if domain.startswith("http://"):
        raise ValueError(f"Insecure HTTP domain rejected: {domain}. Use HTTPS instead.")

    # If domain already includes protocol, use as-is
    if domain.startswith("https://"):
        return domain

    # Otherwise, assume HTTPS and add /api/v1 path
    return f"https://{domain}/api/v1"
