from rest_framework.throttling import SimpleRateThrottle
class ForLoginRateThrottle(SimpleRateThrottle):
    scope = 'for_login'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }