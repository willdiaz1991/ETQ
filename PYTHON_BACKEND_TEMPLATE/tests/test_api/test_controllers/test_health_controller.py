import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from api.response.api_response import ApiResponse


@pytest.mark.asyncio
@patch("api.controllers.health_controller.get_db_session")
@patch("api.controllers.health_controller.get_available_databases")
@patch("api.controllers.health_controller.logger.log_information")
async def test_health_check_all_success(mock_log_info, mock_get_dbs, mock_get_db_session):
    """
    Test that verifies a successful ApiResponse (200 OK) is returned
    when all configured databases respond without errors.
    """
    from api.controllers.health_controller import health_check_all

    mock_get_dbs.return_value = ["sgl", "wms_hc"]

    mock_session = MagicMock()
    mock_session.execute.return_value = None
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    response = await health_check_all()

    assert isinstance(response, ApiResponse)
    assert response.is_successful is True
    assert response.is_error is False
    assert response.result == "All databases are healthy"
    assert response.meta is None
    mock_log_info.assert_called_once()
    assert mock_session.execute.call_count == 2


@pytest.mark.asyncio
@patch("api.controllers.health_controller.get_db_session")
@patch("api.controllers.health_controller.get_available_databases")
@patch("api.controllers.health_controller.logger.log_error")
async def test_health_check_all_partial_failure(mock_log_error, mock_get_dbs, mock_get_db_session):
    """
    Test that verifies a 503 response with an ApiResponse is returned
    when at least one database fails during the health check.
    """
    from api.controllers.health_controller import health_check_all

    mock_get_dbs.return_value = ["sgl", "wms_hc"]

    mock_success = MagicMock()
    mock_success.execute.return_value = None

    mock_failure = MagicMock()
    mock_failure.execute.side_effect = OperationalError("SELECT 1", {}, Exception("DB down"))

    def mock_context(session):
        class MockSessionContext:
            def __enter__(self):
                return session

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return MockSessionContext()

    mock_get_db_session.side_effect = [mock_context(mock_success), mock_context(mock_failure)]

    response = await health_check_all()

    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    body = json.loads(response.body)
    assert body["isSuccessful"] is False
    assert body["isError"] is True
    assert "Failed DBs: wms_hc" in body["errorMessage"]
    assert body["meta"] is None
    assert body["result"] is None
    mock_log_error.assert_called_once()


@pytest.mark.asyncio
@patch("api.controllers.health_controller.get_available_databases", side_effect=RuntimeError("Database setup failed"))
@patch("api.controllers.health_controller.logger.log_error")
async def test_health_check_initialization_failure_returns_service_unavailable(mock_log_error, mock_get_dbs):
    from api.controllers.health_controller import health_check_all

    response = await health_check_all()

    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    body = json.loads(response.body)
    assert body["isSuccessful"] is False
    assert body["isError"] is True
    assert body["errorMessage"] == "Could not initialize the database health check"
    mock_log_error.assert_called_once()
