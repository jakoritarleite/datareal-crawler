from __future__ import annotations

from tldextract import TLDExtract
from urllib.parse import urlparse
from urllib.parse import urldefrag
from w3lib.url import add_or_replace_parameter
from re import compile as _compile, IGNORECASE, match 

def escape_ajax(url: str) -> str:
    """Docstring for the escape_ajax function.
    
    Escape special characters to make AJAX requests.

    Args:
        param1 (str) url:
            The url to escape the AJAX

    Returns:
        Escaped url (str).
    """
    defrag, frag = urldefrag(url)
    if not frag.startswith('!'):
        return url

    return add_or_replace_parameter(defrag, '_escaped_fragment_', frag[1:])

# This function is from DJango Framework, so I'll not create a Docstring for it
def validator(url: str) -> bool:
    regex = _compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', IGNORECASE)

    do_match = match(regex, url)

    if do_match:
        return True

    else:
        return False

def extract_domain(url: str) -> Domain[str]:
    """Docstring for the _extract_domain function.

    Get the domain from a given url.

    Args:
        param1 (str) url:
            The url to get the domain from

    Returns:
        The domain from the url (str)
    """
    extractor: ClassVar[T]
    try:
        extractor = TLDExtract(cache_file=False)

    except TypeError:
        extractor = TLDExtract(cache_dir=False)

    extracted = extractor(url)

    domain: str = f'{extracted.domain}.{extracted.suffix}'

    return domain

def extract_path(url: str) -> Path[str]:
    """Docstring for the _extract_domain function.

    Get the domain from a given url.

    Args:
        param1 (str) url:
            The url to get the domain from

    Returns:
        The domain from the url (str)
    """
    extracted = urlparse(url)

    path: str = extracted.path

    return path