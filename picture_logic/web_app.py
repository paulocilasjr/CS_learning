from __future__ import annotations

import json
import secrets
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from game_core.persistence import ProgressStore
from game_core.planning import ExecutionPlan
from picture_logic.engine import PicturePlanSession
from picture_logic.missions import ACTION_CARDS, PictureMission, build_picture_missions
from picture_logic.settings import PICTURE_SAVE_FILE


WEB_ROOT = Path(__file__).with_name("web")


def _mission_payload(mission: PictureMission) -> dict[str, object]:
    return {
        "number": mission.number,
        "name": mission.name,
        "skill": mission.skill,
        "story": mission.story,
        "instruction": mission.instruction,
        "width": mission.width,
        "height": mission.height,
        "start": list(mission.start),
        "facing": mission.facing,
        "goal": list(mission.goal),
        "obstacles": [list(position) for position in sorted(mission.obstacles)],
        "stars": [list(position) for position in sorted(mission.stars)],
        "cards": list(mission.cards),
        "hints": list(mission.hints),
        "starter_plan": list(mission.starter_plan),
        "max_steps": mission.max_steps,
    }


def _card_payload() -> dict[str, dict[str, str]]:
    return {
        key: {
            "picture": card.picture,
            "name": card.name,
            "spoken_name": card.spoken_name,
        }
        for key, card in ACTION_CARDS.items()
    }


def build_game_page(config: dict[str, object]) -> str:
    template = (WEB_ROOT / "template.html").read_text(encoding="utf-8")
    style = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")
    script = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
    safe_config = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")
    return (
        template.replace("__GAME_STYLE__", style)
        .replace("__GAME_CONFIG__", safe_config)
        .replace("__GAME_SCRIPT__", script)
    )


class _GameServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        handler: type[BaseHTTPRequestHandler],
        *,
        token: str,
        page: str,
        missions: list[PictureMission],
        save_enabled: bool,
    ) -> None:
        super().__init__(address, handler)
        self.token = token
        self.page = page.encode("utf-8")
        self.missions = missions
        self.save_enabled = save_enabled
        self.progress_store = ProgressStore(PICTURE_SAVE_FILE)
        self.picture_session: PicturePlanSession | None = None


class _GameRequestHandler(BaseHTTPRequestHandler):
    server: _GameServer

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == f"/{self.server.token}/":
            self._send_bytes(HTTPStatus.OK, self.server.page, "text/html; charset=utf-8")
            return
        if self.path.endswith("/favicon.ico"):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        api_root = f"/{self.server.token}/api"
        if not self.path.startswith(api_root):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        try:
            payload = self._read_json()
            if self.path == f"{api_root}/run/start":
                self._start_plan(payload)
            elif self.path == f"{api_root}/run/next":
                self._run_next_step()
            elif self.path == f"{api_root}/progress":
                self._save_progress(payload)
            elif self.path == f"{api_root}/close":
                self._send_json(HTTPStatus.OK, {"closed": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown game action."})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def _start_plan(self, payload: dict[str, Any]) -> None:
        mission_index = int(payload["mission"])
        if not 0 <= mission_index < len(self.server.missions):
            raise ValueError("Unknown picture mission.")
        mission = self.server.missions[mission_index]
        actions = payload["plan"]
        if not isinstance(actions, list) or not actions:
            raise ValueError("A picture plan needs at least one card.")
        if len(actions) > mission.max_steps:
            raise ValueError("The picture plan has too many steps.")
        if any(not isinstance(action, str) or action not in mission.cards for action in actions):
            raise ValueError("The plan contains a card that is unavailable in this mission.")

        plan = ExecutionPlan()
        for action in actions:
            plan.add(action, source="picture")
        self.server.picture_session = PicturePlanSession(mission, plan)
        self._send_json(
            HTTPStatus.OK,
            {"world": self.server.picture_session.world.to_dict(), "steps": len(plan.steps)},
        )

    def _run_next_step(self) -> None:
        session = self.server.picture_session
        if session is None:
            self._send_json(HTTPStatus.CONFLICT, {"error": "Start a plan before running a step."})
            return
        progress = session.advance()
        if progress is None:
            self._send_json(HTTPStatus.CONFLICT, {"error": "That plan already finished."})
            return
        result = progress.result
        self._send_json(
            HTTPStatus.OK,
            {
                "action": progress.step.raw,
                "index": progress.index,
                "total": progress.total,
                "message": result.message,
                "error": result.error,
                "finished": progress.finished,
                "complete": session.complete,
                "world": session.world.to_dict(),
            },
        )

    def _save_progress(self, payload: dict[str, Any]) -> None:
        if self.server.save_enabled:
            current_index = int(payload["current_index"])
            badges = int(payload["badges"])
            if not 0 <= current_index <= len(self.server.missions):
                raise ValueError("Invalid picture progress.")
            if not 0 <= badges <= len(self.server.missions):
                raise ValueError("Invalid badge count.")
            self.server.progress_store.save(
                {"version": 2, "current_index": current_index, "badges": badges}
            )
        self._send_json(HTTPStatus.OK, {"saved": self.server.save_enabled})

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 100_000:
            raise ValueError("Game request is too large.")
        data = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("Game request must be an object.")
        return data

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, data, "application/json; charset=utf-8")

    def _send_bytes(self, status: HTTPStatus, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def launch_picture_browser(
    *,
    save_enabled: bool,
    start_level: int | None,
    reset_progress: bool,
    open_browser: Callable[[str], bool] = webbrowser.open_new_tab,
) -> bool:
    missions = build_picture_missions()
    start_index = max(0, (start_level - 1) if start_level else 0)
    start_index = min(start_index, len(missions) - 1)
    token = secrets.token_urlsafe(18)
    server = _GameServer(
        ("127.0.0.1", 0),
        _GameRequestHandler,
        token=token,
        page="",
        missions=missions,
        save_enabled=save_enabled,
    )
    if reset_progress and save_enabled:
        server.progress_store.clear()
    saved_progress = server.progress_store.load() if save_enabled else None
    if saved_progress is not None and "badges" not in saved_progress:
        try:
            old_badges = int(
                saved_progress.get("stars", saved_progress.get("current_index", 0))
            )
        except (TypeError, ValueError):
            old_badges = 0
        saved_progress["badges"] = min(max(old_badges, 0), len(missions))
    api_base = f"/{token}/api"
    config = {
        "missions": [_mission_payload(mission) for mission in missions],
        "cards": _card_payload(),
        "saveEnabled": save_enabled,
        "savedProgress": saved_progress,
        "startIndex": start_index,
        "explicitStart": start_level is not None,
        "stepDelayMs": 720,
        "apiBase": api_base,
    }
    server.page = build_game_page(config).encode("utf-8")
    url = f"http://127.0.0.1:{server.server_port}/{token}/"
    if not open_browser(url):
        server.server_close()
        return False

    timeout = threading.Timer(4 * 60 * 60, server.shutdown)
    timeout.daemon = True
    timeout.start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        timeout.cancel()
        server.server_close()
    return True
