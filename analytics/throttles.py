from rest_framework.throttling import AnonRateThrottle


class PageViewRateThrottle(AnonRateThrottle):
    """Limit page-view recording to prevent abuse."""

    scope = 'page_views'
