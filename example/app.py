from dataclasses import dataclass
from example.schema import SimpleID
from src.flask_typescript.generator import register_command
from src.flask_typescript.decorator import generate_ts_client
from flask import Flask


@dataclass(frozen=True)
class CustomResponse:
    id: int


@dataclass(frozen=True)
class ExampleType:
    id: int
    name: str


@dataclass(frozen=True)
class PayloadExample:
    scope: str
    name: str


@dataclass(frozen=True)
class LengthResponse:
    size: int


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    # might change this API
    register_command(app)

    @app.route("/")
    @generate_ts_client
    def index() -> CustomResponse:
        return CustomResponse(id=0)

    # This currently isn't supported in the client generation
    @app.route("/<int:custom_id>")
    @generate_ts_client
    def params(custom_id: int) -> CustomResponse:
        return CustomResponse(id=custom_id)

    @app.route("/via_query")
    @generate_ts_client
    def query(custom_id: int) -> ExampleType:
        return ExampleType(id=custom_id, name="hello")

    @app.route("/number")
    @generate_ts_client
    def number(custom_id: int) -> SimpleID:
        return SimpleID(id=custom_id)

    @app.route("/post", methods=["POST"])
    @generate_ts_client
    def post(payload: PayloadExample) -> LengthResponse:
        return LengthResponse(size=len(payload.name))

    @app.route("/naming", methods=["POST"])
    @generate_ts_client
    def naming_second(payload: PayloadExample, idz: SimpleID) -> ExampleType:
        return ExampleType(id=3, name=payload.name)

    @app.route("/exclude")
    def excluded():
        return "hi"


    return app
