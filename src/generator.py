from dataclasses import is_dataclass
from distutils.command.build import build
import inspect
from itertools import groupby
from pathlib import Path
from pprint import pprint
from subprocess import check_output
from typing import Sequence, Set
import click
from flask import current_app, g
from flask.cli import with_appcontext
from jinja2 import Environment, FileSystemLoader, Template
from werkzeug.routing import Rule

TYPE_MAPPING = {int: "number", str: "string"}


def register_command(app) -> None:
    app.cli.add_command(generate_typescript)


@click.command()
@with_appcontext
@click.option("--clean", is_flag=True)
def generate_typescript(clean: bool) -> None:
    """
    generate typescript types
    """
    env = Environment(loader=FileSystemLoader("src/templates"))
    if clean:
        click.secho("Cleaning generated files", fg="red")
        check_output(["rm", "-r", "./typescript/generated"])

    click.secho("Generating typescript interfaces for views", fg="yellow")
    build_interfaces(env)
    click.secho("Generating typescript api client", fg="yellow")
    build_api_definition(env)


def build_api_definition(env: Environment) -> None:
    for rule in current_app.url_map.iter_rules():
        sig = inspect.signature(current_app.view_functions[rule.endpoint])
        _generate_typed_call(sig, rule)


def _generate_typed_call(sig: inspect.Signature, rule: Rule) -> None:
    type_name = f"{rule.endpoint.capitalize()}Request"
    print(type_name)
    print(
        {
            name: TYPE_MAPPING.get(t.annotation, t.annotation.__name__)
            for name, t in sig.parameters.items()
        }
    )


def build_interfaces(env: Environment) -> None:
    interfaces: Set[object] = set()
    for name, view in current_app.view_functions.items():
        sig = inspect.signature(view)

        # Add all dataclasses to interfaces to have types generated
        if is_dataclass(sig.return_annotation):
            interfaces.add(sig.return_annotation)
        for param in sig.parameters.values():
            if is_dataclass(param.annotation):
                interfaces.add(param.annotation)

    def g(i):
        return i.__module__

    template = env.get_template("interface.ts")
    for mod, iterfac in groupby(sorted(list(interfaces), key=g), g):
        types = _generate_interface(template, list(iterfac))
        _write_interfaces(mod, types)


def _generate_interface(template: Template, dataclasses: Sequence[object]) -> str:
    # TODO: generate these in a predictable order
    return template.render(
        interfaces=[
            dict(
                name=dataclass.__name__,
                attributes={
                    field: TYPE_MAPPING.get(tfield, "any")
                    for field, tfield in dataclass.__annotations__.items()
                },
            )
            for dataclass in dataclasses
        ],
    )


def _write_interfaces(module: str, data: str) -> None:
    # Move to config
    path = Path.cwd() / "typescript" / "generated" / "interfaces"
    path = path.joinpath(module.replace(".", "/"))
    path.mkdir(parents=True, exist_ok=True)
    interface = path / f"types.ts"
    with (path / interface).open("w+") as file:
        file.write(data)
