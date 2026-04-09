from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, meals, workouts, metrics, ai, profiles
from middleware.rate_limit import RateLimitMiddleware
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='FitForge API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# RateLimitMiddleware is requested in plan but not yet implemented. 
# Creating a placeholder to avoid import errors until it's developed.
try:
    from middleware.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)
except ImportError:
    logger.warning("RateLimitMiddleware not found, skipping.")

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(meals.router, prefix='/meals', tags=['meals'])
app.include_router(metrics.router, prefix='/metrics', tags=['metrics'])
app.include_router(ai.router, prefix='/ai', tags=['ai'])
app.include_router(workouts.router, prefix='/workouts', tags=['workouts'])
app.include_router(profiles.router, prefix='/profiles', tags=['profiles'])

@app.get('/health')
async def health():
    logger.info("Health check pinged")
    return {'status': 'ok'}
