import pytest
from unittest.mock import MagicMock

# ============================================================================
# TEMPLATE: Python + Pytest (AAA Pattern, Fixtures & Parameterization)
# ============================================================================

@pytest.fixture
def mock_external_client():
    """Only mock external boundary services (Network/DB/Third-party)."""
    client = MagicMock()
    client.request.return_value = {"status": "ok", "id": "tx_456"}
    return client

class TestServiceUnderTest:
    # ------------------------------------------------------------------------
    # Dimension 1: Happy Path
    # ------------------------------------------------------------------------
    def test_nominal_execution_success(self, mock_external_client):
        # Arrange
        service = PaymentService(gateway=mock_external_client)
        payload = {"amount": 50, "currency": "USD"}

        # Act
        result = service.process(payload)

        # Assert
        assert result["status"] == "ok"
        assert result["id"] == "tx_456"
        mock_external_client.request.assert_called_once()

    # ------------------------------------------------------------------------
    # Dimension 2: Boundary & Limits (Parameterized)
    # ------------------------------------------------------------------------
    @pytest.mark.parametrize("invalid_amount,expected_exception", [
        (0, ValueError),
        (-10, ValueError),
        (1_000_001, OverflowError),
    ])
    def test_amount_boundary_validation(self, mock_external_client, invalid_amount, expected_exception):
        # Arrange
        service = PaymentService(gateway=mock_external_client)

        # Act & Assert
        with pytest.raises(expected_exception):
            service.process({"amount": invalid_amount, "currency": "USD"})

    # ------------------------------------------------------------------------
    # Dimension 3 & 4: Nullability and Failure Modes
    # ------------------------------------------------------------------------
    def test_gateway_connection_timeout_raises_custom_error(self, mock_external_client):
        # Arrange
        mock_external_client.request.side_effect = TimeoutError("Connection timed out")
        service = PaymentService(gateway=mock_external_client)

        # Act & Assert
        with pytest.raises(ServiceUnavailableError):
            service.process({"amount": 100, "currency": "USD"})
