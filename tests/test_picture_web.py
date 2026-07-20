from __future__ import annotations

import json
import threading
import unittest
from urllib.request import Request, urlopen

from picture_logic.web_app import build_game_page, launch_picture_browser


class PictureWebTests(unittest.TestCase):
    def test_page_contains_click_controls_and_no_template_placeholders(self) -> None:
        page = build_game_page(
            {
                "missions": [],
                "cards": {},
                "saveEnabled": False,
                "savedProgress": None,
                "startIndex": 0,
                "explicitStart": False,
                "stepDelayMs": 0,
                "apiBase": "/test/api",
            }
        )

        self.assertIn("TAP PICTURE CARDS", page)
        self.assertIn("TRY MY PLAN", page)
        self.assertIn("READ TO ME", page)
        self.assertNotIn("__GAME_", page)

    def test_browser_api_runs_plan_through_python_stepper(self) -> None:
        failures: list[BaseException] = []
        completed: list[bool] = []
        client_thread: threading.Thread | None = None

        def post(url: str, payload: dict[str, object]) -> dict[str, object]:
            request = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))

        def open_browser(url: str) -> bool:
            nonlocal client_thread

            def play() -> None:
                try:
                    with urlopen(url, timeout=5) as response:
                        self.assertIn("BB-8 PICTURE PLAN ADVENTURE", response.read().decode("utf-8"))
                    api = f"{url.rstrip('/')}/api"
                    post(f"{api}/run/start", {"mission": 0, "plan": ["forward"]})
                    step = post(f"{api}/run/next", {})
                    completed.append(bool(step["complete"]))
                    post(f"{api}/close", {})
                except BaseException as exc:  # pragma: no cover - re-raised in test thread
                    failures.append(exc)

            client_thread = threading.Thread(target=play, daemon=True)
            client_thread.start()
            return True

        launched = launch_picture_browser(
            save_enabled=False,
            start_level=1,
            reset_progress=False,
            open_browser=open_browser,
        )
        assert client_thread is not None
        client_thread.join(timeout=5)

        if failures:
            raise failures[0]
        self.assertTrue(launched)
        self.assertEqual(completed, [True])


if __name__ == "__main__":
    unittest.main()
