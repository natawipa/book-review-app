from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical_host = getattr(settings, "CANONICAL_HOST", "")
        canonical_scheme = getattr(settings, "CANONICAL_SCHEME", request.scheme)

        if canonical_host and request.get_host() != canonical_host:
            target_url = f"{canonical_scheme}://{canonical_host}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(target_url)

        return self.get_response(request)
