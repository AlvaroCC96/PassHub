import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
