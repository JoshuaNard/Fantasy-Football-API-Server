import json

from web_scraping.base import PlayerRecord
from web_scraping.debug import records_as_json


def test_records_as_json_prints_every_normalized_field():
    records = [
        PlayerRecord(
            external_id="josh-allen",
            full_name="Josh Allen",
            position="QB",
            team="BUF",
            attributes={"rank": 1, "salary_cap_value": 29},
        )
    ]

    output = records_as_json(records)

    assert json.loads(output) == [
        {
            "external_id": "josh-allen",
            "full_name": "Josh Allen",
            "first_name": "",
            "last_name": "",
            "position": "QB",
            "team": "BUF",
            "active": True,
            "attributes": {"rank": 1, "salary_cap_value": 29},
        }
    ]
    assert "\n  {" in output


def test_records_as_json_only_prints_first_ten_players():
    records = [
        PlayerRecord(external_id=str(index), full_name=f"Player {index}")
        for index in range(1, 12)
    ]

    output = json.loads(records_as_json(records))

    assert len(output) == 10
    assert output[0]["full_name"] == "Player 1"
    assert output[-1]["full_name"] == "Player 10"
