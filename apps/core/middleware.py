import hashlib
import threading
from ua_parser import user_agent_parser

_local = threading.local()

SKIP_PATHS = ('/admin/', '/api/', '/static/', '/media/', '/favicon', '/__debug__', '/ckeditor5/')
SKIP_EXTENSIONS = ('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.map')


def _should_skip(path: str) -> bool:
    for prefix in SKIP_PATHS:
        if path.startswith(prefix):
            return True
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return True
    return False


def _parse_ua(ua_string: str) -> dict:
    if not ua_string:
        return {'browser': '', 'browser_ver': '', 'os': '', 'device_type': 'other'}
    parsed = user_agent_parser.Parse(ua_string)
    browser = parsed['user_agent']['family']
    browser_ver = parsed['user_agent']['major'] or ''
    os_name = parsed['os']['family']
    device = parsed['device']['family']

    if browser in ('Spider', 'bot', 'Googlebot', 'Bingbot') or 'bot' in ua_string.lower():
        device_type = 'bot'
    elif device in ('iPhone', 'Android', 'BlackBerry') or 'Mobile' in ua_string:
        device_type = 'mobile'
    elif device == 'iPad' or 'Tablet' in ua_string:
        device_type = 'tablet'
    elif browser == 'Other' and os_name == 'Other':
        device_type = 'bot'
    else:
        device_type = 'desktop'

    return {
        'browser': browser,
        'browser_ver': browser_ver,
        'os': os_name,
        'device_type': device_type,
    }


def _get_ip(request) -> str:
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:32] if ip else ''


def _get_country(request) -> str:
    # Cloudflare header (when deployed behind CF)
    return (
        request.META.get('HTTP_CF_IPCOUNTRY', '')
        or request.META.get('HTTP_X_COUNTRY', '')
        or ''
    )


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path
        if _should_skip(path):
            return response

        # Only track successful HTML page loads (not API, not errors)
        if response.status_code not in (200, 301, 302):
            return response

        # Skip if it looks like an API call (JSON response)
        ct = response.get('Content-Type', '')
        if 'json' in ct or 'xml' in ct:
            return response

        try:
            ua_info = _parse_ua(request.META.get('HTTP_USER_AGENT', ''))
            if ua_info['device_type'] == 'bot':
                return response

            from apps.core.models import PageView
            PageView.objects.create(
                path=path[:500],
                browser=ua_info['browser'][:60],
                browser_ver=ua_info['browser_ver'][:20],
                os=ua_info['os'][:60],
                device_type=ua_info['device_type'],
                country=_get_country(request)[:80],
                ip_hash=_hash_ip(_get_ip(request)),
                referrer=request.META.get('HTTP_REFERER', '')[:500],
                session_key=(request.session.session_key or '')[:64],
            )
        except Exception:
            pass  # Never break the request

        return response
