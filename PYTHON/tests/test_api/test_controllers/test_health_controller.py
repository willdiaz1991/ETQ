from fastapi.testclient import TestClient

from api.main import create_app


def test_health_check_reports_api_availability_without_external_databases():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "errorMessage": None,
        "isError": False,
        "isSuccessful": True,
        "messages": None,
        "result": "API disponible",
        "meta": None,
    }
