import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from main import app
from database import supabase
from jose import jwt
from config import settings

# --- Test Configuration ---
BASE_URL = "http://testserver"
MOCK_USER_ID = "00000000-0000-0000-0000-000000000000"
MOCK_TOKEN = jwt.encode({"sub": MOCK_USER_ID}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@pytest.fixture
async def async_client():
    async with httpx.AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {MOCK_TOKEN}"}

# --- Auth Tests ---

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_register(async_client):
    # Mock Supabase auth registration
    with patch("database.supabase.auth.sign_up", new_callable=AsyncMock) as mock_signup:
        mock_signup.return_value = MagicMock(
            user=MagicMock(id=MOCK_USER_ID, email="test@example.com"),
            session=MagicMock(access_token="mock_token")
        )

        payload = {"email": "test@example.com", "password": "password123", "username": "testuser"}
        response = await async_client.post("/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user" in data
        assert "session" in data
        assert data["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login(async_client):
    with patch("database.supabase.auth.sign_in_with_password", new_callable=AsyncMock) as mock_login:
        mock_login.return_value = MagicMock(
            user=MagicMock(id=MOCK_USER_ID, email="test@example.com"),
            session=MagicMock(access_token="mock_token")
        )

        payload = {"email": "test@example.com", "password": "password123"}
        response = await async_client.post("/auth/login", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user" in data
        assert "session" in data

# --- Security Tests ---

@pytest.mark.asyncio
async def test_unauthorized_access(async_client):
    # Test a protected route without token
    response = await async_client.get("/profiles/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_expired_token(async_client):
    # Use a token with invalid signature (wrong key)
    bad_token = jwt.encode({"sub": MOCK_USER_ID}, "wrong_key", algorithm=settings.JWT_ALGORITHM)
    response = await async_client.get("/profiles/me", headers={"Authorization": f"Bearer {bad_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --- Profiles Tests ---

@pytest.mark.asyncio
async def test_get_profile_me(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{"id": MOCK_USER_ID, "username": "testuser", "full_name": "Test User"}]
        )

        response = await async_client.get("/profiles/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_update_profile_me(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": MOCK_USER_ID, "username": "testuser", "calorie_goal": 2500}]
        )

        payload = {"calorie_goal": 2500}
        response = await async_client.patch("/profiles/me", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["calorie_goal"] == 2500

# --- Meals Tests ---

@pytest.mark.asyncio
async def test_create_meal(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "meal-123", "name": "Chicken Rice", "calories": 500}]
        )

        payload = {
            "name": "Chicken Rice",
            "calories": 500,
            "protein_g": 40,
            "carbs_g": 50,
            "fat_g": 10,
            "fiber_g": 5,
            "meal_type": "lunch"
        }
        response = await async_client.post("/meals", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == "meal-123"

@pytest.mark.asyncio
async def test_get_meals_by_date(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "meal-1", "name": "Oatmeal", "calories": 300}]
        )

        response = await async_client.get("/meals?date=2026-04-08", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Oatmeal"

@pytest.mark.asyncio
async def test_delete_meal(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )

        response = await async_client.delete("/meals/meal-123", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

# --- Workouts Tests ---

@pytest.mark.asyncio
async def test_create_workout(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        # Mock workout insert
        mock_table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "workout-123", "name": "Push Day"}]
        )

        payload = {
            "name": "Push Day",
            "type": "strength",
            "duration_min": 60,
            "calories_burned": 400,
            "exercises": [
                {"exercise_name": "Bench Press", "sets": 3, "reps": 10, "weight_kg": 80, "rest_sec": 90, "order_index": 0}
            ]
        }
        response = await async_client.post("/workouts", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == "workout-123"

@pytest.mark.asyncio
async def test_get_workouts_by_date(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "workout-1", "name": "Leg Day"}]
        )

        response = await async_client.get("/workouts?date=2026-04-08", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["name"] == "Leg Day"

# --- Metrics Tests ---

@pytest.mark.asyncio
async def test_log_metrics(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "met-1", "weight_kg": 75.0}]
        )

        payload = {"weight_kg": 75.0, "body_fat_pct": 15.0}
        response = await async_client.post("/metrics", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.asyncio
async def test_water_log(async_client, auth_headers):
    with patch("database.supabase.table") as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "wat-1", "glasses": 1}]
        )

        response = await async_client.post("/water-log", json={"glasses": 1}, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

# --- AI Tests (Mocking Fallbacks) ---

@pytest.mark.asyncio
async def test_ai_chat_fallback_logic(async_client, auth_headers):
    # Mock AI Router services
    with patch("routers.ai.ai_router") as mock_ai_router:
        # Scenario: Groq fails, falls back to Gemini
        mock_ai_router.chat.return_value = {"content": "Gemini response", "provider": "gemini"}

        payload = {"message": "Hi", "history": []}
        response = await async_client.post("/ai/chat", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["provider"] == "gemini"
        assert response.json()["content"] == "Gemini response"

@pytest.mark.asyncio
async def test_ai_workout_plan(async_client, auth_headers):
    with patch("routers.ai.ai_router") as mock_ai_router:
        mock_ai_router.generate_workout_plan.return_value = {"content": "Plan content", "provider": "groq"}

        payload = {"muscle_group": "chest", "experience_level": "intermediate"}
        response = await async_client.post("/ai/workout-plan", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["provider"] == "groq"

@pytest.mark.asyncio
async def test_ai_meal_suggestion(async_client, auth_headers):
    with patch("routers.ai.ai_router") as mock_ai_router:
        mock_ai_router.suggest_meal.return_value = {"content": "Meal content", "provider": "groq"}

        payload = {"message": "High protein dinner"}
        response = await async_client.post("/ai/meal-suggestion", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["provider"] == "groq"
