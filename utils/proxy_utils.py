"""
Utility functions for handling proxy configurations.
"""
import logging
from typing import Dict, Optional, Union
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

def normalize_proxy_url(proxy_url: str) -> str:
    """
    Ensures that a proxy URL has a proper scheme prefix.
    
    Args:
        proxy_url: The proxy URL to normalize
        
    Returns:
        A normalized proxy URL with a scheme prefix
    """
    if not proxy_url:
        return proxy_url
        
    if "://" not in proxy_url:
        normalized_url = f"http://{proxy_url}"
        logger.debug(f"Added http:// prefix to proxy URL: {normalized_url}")
        return normalized_url
    return proxy_url

def create_httpx_transport(proxy: Optional[Union[str, Dict[str, str]]]) -> Optional[Dict[str, httpx.HTTPTransport]]:
    """
    Creates httpx transport mounts for the given proxy configuration.
    
    Args:
        proxy: Proxy configuration, can be a string URL or a dictionary mapping schemes to URLs
        
    Returns:
        A dictionary of mounts for httpx client or None if no proxy is provided
    """
    if not proxy:
        return None
        
    mounts = {}
    
    if isinstance(proxy, str):
        proxy_url = normalize_proxy_url(proxy)
        mounts["http://"] = httpx.HTTPTransport(proxy=proxy_url)
        mounts["https://"] = httpx.HTTPTransport(proxy=proxy_url)
    elif isinstance(proxy, dict):
        for scheme, url in proxy.items():
            if scheme in ["http://", "https://"]:
                mounts[scheme] = httpx.HTTPTransport(proxy=normalize_proxy_url(url))
    
    return mounts if mounts else None

def create_httpx_client(proxy: Optional[Union[str, Dict[str, str]]], **kwargs) -> httpx.Client:
    """
    Creates an httpx client with the given proxy configuration.
    
    Args:
        proxy: Proxy configuration, can be a string URL or a dictionary mapping schemes to URLs
        **kwargs: Additional arguments to pass to the httpx.Client constructor
        
    Returns:
        An httpx client configured with the given proxy
    """
    client_kwargs = kwargs.copy()
    
    mounts = create_httpx_transport(proxy)
    if mounts:
        client_kwargs["mounts"] = mounts
        
    return httpx.Client(**client_kwargs)
