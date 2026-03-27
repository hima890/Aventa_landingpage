from rest_framework.throttling import AnonRateThrottle


class SubmissionRateThrottle(AnonRateThrottle):
    """Limit waitlist submission creation to prevent spam."""

    scope = 'submissions'
