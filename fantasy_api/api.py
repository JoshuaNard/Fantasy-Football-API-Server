from ninja import NinjaAPI

from draft.api import router as draft_router


api = NinjaAPI(
    title="Fantasy Football API",
    version="0.1.0",
    description="API backing the FantasyFootballDraftAssist frontend.",
)


api.add_router("", draft_router)
