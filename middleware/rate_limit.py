from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, dispatch):
        super().__init__(dispatch)
        # user_id -> [timestamps]
        self.requests = defaultdict(list)
        self.limit = 20 # requests per hour
        self.window = 3600 # 1 hour

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith('/ai'):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                user_key = request.client.host
            else:
                token = auth_header.split(' ')[1]
                import jwt
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    user_key = payload.get('sub', request.client.host)
                except Exception:
                    user_key = request.client.host

            now = time.time()
            user_requests = self.requests[user_key]
            self.requests[user_key] = [t for t in user_requests if t > now - self.window]

            if len(self.requests[user_key]) >= self.limit:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Rate limit exceeded for user/IP: {user_key}")
                raise HTTPException(status_code=429, detail="AI request limit reached (20/hr). Please try again later.")

            self.requests[user_key].append(now)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"AI request accepted for user/IP: {user_key}. Count: {len(self.requests[user_key])}/{self.limit}")

        return await call_next(request)
