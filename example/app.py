from dataclasses import dataclass
from src.decorator import client_typed
from flask import Flask


@dataclass(frozen=True)
class CustomResponse:
    id: int


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    @app.get("/")
    @client_typed
    def index() -> CustomResponse:
        return CustomResponse(id=0)

    @app.get("/<int:custom_id>")
    @client_typed
    def params(custom_id: int) -> CustomResponse:
        return CustomResponse(id=custom_id)

    @app.get("/via_query")
    @client_typed
    def query(custom_id: int) -> CustomResponse:
        return CustomResponse(id=custom_id)

    return app
