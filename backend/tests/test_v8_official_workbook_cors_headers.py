from __future__ import annotations

from fastapi import Response
from fastapi.testclient import TestClient

from app.main import create_app

EXPOSED_OFFICIAL_WORKBOOK_HEADERS = {
    "content-disposition",
    "x-fpms-artifact-id",
    "x-fpms-content-sha256",
    "x-fpms-template-version",
    "x-fpms-template-content-sha256",
    "x-fpms-workbook-input-version-id",
    "x-fpms-workbook-disposition",
    "x-fpms-generated-status",
}


def test_official_workbook_metadata_is_exposed_to_allowed_browser_origins() -> None:
    app = create_app()

    @app.get("/_test/official-workbook-response")
    def official_workbook_response() -> Response:
        return Response(
            content=b"controlled-test-workbook",
            headers={header: "test" for header in EXPOSED_OFFICIAL_WORKBOOK_HEADERS},
        )

    with TestClient(app) as client:
        for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
            response = client.get(
                "/_test/official-workbook-response",
                headers={"Origin": origin},
            )

            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origin
            exposed = {
                header.strip().lower()
                for header in response.headers["access-control-expose-headers"].split(",")
            }
            assert exposed == EXPOSED_OFFICIAL_WORKBOOK_HEADERS
