import pytest


@pytest.fixture
def demo_run(db):
    from market.services.demo_data import create_demo_search_run

    return create_demo_search_run()
