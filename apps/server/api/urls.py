from market.api import router as market_router
from ninja import NinjaAPI

api = NinjaAPI(title="Jarjour Market Intelligence API", version="1.0.0")


@api.get("/health")
def health(request):
    return {"status": "ok", "service": "jarjour-market-intelligence"}


api.add_router("/", market_router)
