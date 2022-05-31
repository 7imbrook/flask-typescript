from dataclasses import dataclass
from example.schema import SimpleID
from src.generator import register_command
from src.decorator import client_typed
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

    @app.route("/")
    @client_typed
    def index() -> CustomResponse:
        return CustomResponse(id=0)

    # This currently isn't supported in the client generation
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
    def number(custom_id: int) -> SimpleID:
        return SimpleID(id=custom_id)

    @app.route("/post", methods=["POST"])
    @client_typed
    def post(payload: PayloadExample) -> LengthResponse:
        return LengthResponse(size=len(payload.name))
    
    @app.route("/naming", methods=["POST"])
    @client_typed
    def naming_second(payload: PayloadExample, idz: SimpleID) -> ExampleType:
        return ExampleType(id=3, name=payload.name)
    
    register_command(app)
    
    return app
