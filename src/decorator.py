from atexit import register
from dataclasses import asdict, is_dataclass
import functools
import inspect
from inspect import Signature, _empty
from json import load
from pathlib import Path
from typing import Any, Mapping
import click

from flask import g, has_request_context, request, abort
from jinja2 import Environment, FileSystemLoader, Template

route_types: Mapping[Any, Signature] = {}

TYPE_MAPPING = {int: "number", str: "string"}


def client_typed(flask_route):
    """
    Reads the routes type signature and generates ...something...
    Not push safe for most multi server applications.
    """
    signature = inspect.signature(flask_route)
    return_type = signature.return_annotation
    parameters = signature.parameters

    @functools.wraps(flask_route)
    def _skip(*a, **k):
        return flask_route(*a, **k)

    if return_type is _empty:
        return _skip

    for _, tparam in parameters.items():
        if tparam.annotation is _empty:
            return _skip

    # Register views for later generation
    route_types[flask_route] = signature

    @functools.wraps(flask_route)
    def _inner(*args, **kwargs):
        # Gotta be in a request
        assert has_request_context(), "Missing request context"

        # flask already puts url positional params in kwargs for us
        # we just need to pull any url params or build the post body for more complex types
        new_args = kwargs

        # Check all the params defined in the method and parse them by they're signature
        for param, tparam in parameters.items():
            try:
                if kwargs.get(param):
                    continue
                elif is_dataclass(tparam.annotation):
                    new_args[param] = tparam.annotation(**request.json[param])
                elif discovered := request.args.get(param):
                    new_args[param] = tparam.annotation(discovered)
                else:
                    # TODO check if type is required
                    abort(400, f"Missing required param {tparam}")
            except (ValueError, KeyError, TypeError):
                abort(400, f"Wrong type for {tparam}")

        # Excute the route, TODO allow for raised exceptions for other responses
        response = flask_route(**new_args)

        # Assert and convert
        assert isinstance(response, return_type)
        return asdict(response)

    return _inner


def register_command(app) -> None:
    app.cli.command()(generate_typescript)


def generate_typescript() -> None:
    """
    generate typescript types
    """
    env = Environment(loader=FileSystemLoader("src/templates"))
    template = env.get_template("interface.ts")
    click.secho("Generating typescript interfaces for views", fg="yellow")
    interfaces: Mapping[object, str] = {}

    for _, sig in route_types.items():
        if (
            is_dataclass(sig.return_annotation)
            and sig.return_annotation not in interfaces
        ):
            interfaces[sig.return_annotation] = _generate_interface(
                template, sig.return_annotation
            )

    for klass, data in interfaces.items():
        _write_interfaces(klass, data)


def _generate_interface(template: Template, dataclass: object) -> str:
    return template.render(
        name=dataclass.__name__,
        attributes={
            field: TYPE_MAPPING.get(tfield, "any")
            for field, tfield in dataclass.__annotations__.items()
        },
    )


def _write_interfaces(klass: object, data: str) -> None:
    # Move to config
    path = (
        Path.cwd()
        / "typescript"
        / "generated"
        / "interfaces"
    )
    path = path.joinpath(klass.__module__.replace(".", "/"))
    path.mkdir(parents=True, exist_ok=True)
    interface = path / f"{klass.__name__}.ts"
    with (path / interface ).open('w+') as file:
        file.write(data)

