from urllib.parse import urlsplit

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def redirect_to_referrer(
    request: HttpRequest,
    fallback_target: str,
) -> HttpResponseRedirect:
    """Redirect to a safe referrer, or to the supplied fallback target."""
    referring_url = request.META.get("HTTP_REFERER")
    if (
        referring_url
        and url_has_allowed_host_and_scheme(
            referring_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        and urlsplit(referring_url).path != request.path
    ):
        return redirect(referring_url)
    return redirect(fallback_target)
