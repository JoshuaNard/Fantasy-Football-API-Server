"""Combine normalized player projections from multiple sources."""

from collections import defaultdict
import re
from statistics import median
from typing import Iterable

from web_scraping.base import PlayerRecord


def _player_key(name: str) -> str:
    key = re.sub(r"[^a-z0-9]", "", name.casefold())
    return re.sub(r"(?:jr|sr|ii|iii)$", "", key)


def combine_player_projections(
    source_players: Iterable[tuple[str, list[PlayerRecord]]],
) -> list[dict]:
    """Merge players by name and calculate a median for every available stat."""
    merged = {}
    for source, players in source_players:
        for player in players:
            key = _player_key(player.full_name)
            combined = merged.setdefault(
                key,
                {
                    "player": player.full_name,
                    "team": player.team,
                    "period": player.attributes.get("period", ""),
                    "source_projections": defaultdict(dict),
                },
            )
            if player.team:
                combined["team"] = player.team
            for stat, value in player.attributes.get("projections", {}).items():
                if value is not None:
                    combined["source_projections"][stat][source] = float(value)

    results = []
    for player in merged.values():
        source_projections = {
            stat: dict(values)
            for stat, values in player["source_projections"].items()
        }
        consensus = {
            stat: median(values.values())
            for stat, values in source_projections.items()
        }
        results.append(
            {
                "player": player["player"],
                "team": player["team"],
                "period": player["period"],
                "projections": consensus,
                "source_projections": source_projections,
            }
        )
    return sorted(results, key=lambda player: player["player"])
