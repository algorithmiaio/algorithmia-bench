import pytest

def pytest_addoption(parser):
    parser.addoption("--apiKey", action="store", default=None,
        help="Provide your Algorithmia API Key for testing")
    parser.addoption("--runApiKeyTests", action="store_true",
        help="Run tests that require an API Key")

@pytest.fixture
def apiKey(request):
    return request.config.getoption("--apiKey")