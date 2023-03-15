def pytest_addoption(parser):
    parser.addoption("--host", action="store")
    parser.addoption("--p1", action="store")
    parser.addoption("--p2", action="store")