from dataclasses import dataclass
from src.decorator import client_typed, register_command
from flask import Flask


@dataclass(frozen=True)
class CustomResponse:
    id: int


@dataclass(frozen=True)
class ExampleType:
    id: int
    name: str


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    register_command(app)

    @app.route("/")
    @client_typed
    def index() -> CustomResponse:
        return CustomResponse(id=0)

    @app.route("/<int:custom_id>")
    @client_typed
    def params(custom_id: int) -> CustomResponse:
        return CustomResponse(id=custom_id)

    @app.route("/via_query")
    @client_typed
    def query(custom_id: int) -> ExampleType:
        return ExampleType(id=custom_id, name="hello")

    @app.route("/number")
    @client_typed
    def number(custom_id: int) -> int:
        return custom_id

    return app
