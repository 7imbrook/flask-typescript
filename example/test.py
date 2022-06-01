from dataclasses import dataclass
from flask import Flask
from flask_testing import TestCase

from src.flask_typescript.decorator import generate_ts_client


@dataclass(frozen=True)
class TestReturn:
    name: str


@dataclass(frozen=True)
class TestBody:
    id: int
    token: str


class ClientTypedViewGetTest(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/")
        def t():
            return {}

        return app

    def test_simple_view(self):
        self.assert200(self.client.get("/"), "None decorated function broke")


class DecoratorWithNoTypesTest(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/")
        @generate_ts_client
        def b():
            return {}

        return app

    def test_no_types(self):
        self.assert200(self.client.get("/"), "Untyped failing pass through")


class ViewIsInvalidForFlaskTest(TestCase):
    # TODO: Split this into smaller cases like below
    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TESTING=True)

        @app.get("/")
        def c(p):
            return {}

        return app

    def test_params(self):
        # This is a flask error
        self.assert500(
            self.client.get("/"),
            "Passing function to flask should fail it flask thinks it bad",
        )


class TestPartingURLParams(TestCase):
    # TODO: Split this into smaller cases like below
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/")
        @generate_ts_client
        def d(pa: int) -> TestReturn:
            return TestReturn(name=f"PA:{pa}")

        return app

    def test_params_typed(self):
        self.assert400(
            self.client.get("/"), "Should raise 400 for missing required params"
        )

    def test_params_typed_valid(self):
        response = self.client.get("/?pa=1")
        self.assert200(response, "Parting params should parse this as an int")
        self.assertEqual(
            response.json["name"], "PA:1", "Something went wrong the response"
        )

    def test_params_typed_invalid_type(self):
        response = self.client.get("/?pa=timbrook")
        self.assert400(response, "Type enforcement failed")


class TestParamsWithoutTypeFlaskError(TestCase):
    def create_app(self):
        app = Flask(__name__)

        @app.get("/")
        @generate_ts_client
        def simple(unknown) -> TestReturn:
            return TestReturn(name=f"PA")

        return app

    def test(self):
        self.assert500(self.client.get("/"), "flask should have failed")


class TestPostBodyParsing(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.post("/")
        @generate_ts_client
        def simple(token: TestBody) -> TestReturn:
            return TestReturn(name=f"{token.token}:{token.id}")

        return app

    def test_empty_body(self):
        self.assert400(self.client.post("/", json={}))

    def test_body_missing_keys(self):
        self.assert400(self.client.post("/", json={"token": {}}))

    def test_body_extra_keys(self):
        self.assert400(
            self.client.post(
                "/", json={"token": {"token": "value", "id": 0, "moose": "high"}}
            )
        )

    def test_body(self):
        self.assert200(
            response := self.client.post(
                "/", json={"token": {"token": "value", "id": 0}}
            )
        )
        self.assertEqual(response.json["name"], "value:0")


class TestURIParamsParsing(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/<int:idx>")
        @generate_ts_client
        def simple(idx: int) -> TestReturn:
            return TestReturn(name=f"{idx}")

        return app

    def test_url(self):
        self.assert200(self.client.get("/5"))


class TestMultpleParams(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/<int:idx>")
        @generate_ts_client
        def simple(idx: int, add: int) -> TestReturn:
            return TestReturn(name=f"{idx}")

        return app

    def test_url(self):
        self.assert400(self.client.get("/5"))
    
    def test_with_query(self):
        self.assert200(self.client.get("/5?add=3"))
