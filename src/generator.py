from dataclasses import is_dataclass
from distutils.command.build import build
import inspect
from itertools import chain, groupby
import itertools
import json
from os import sync
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

interface_import_lookup = {}


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
    env.filters["find_dataclass_imports"] = _find_dataclass_imports
    if clean:
        click.secho("Cleaning generated files", fg="red")
        check_output(["rm", "-r", "./typescript/generated"])

    click.secho("Generating typescript interfaces for views", fg="yellow")
    build_interfaces(env)
    click.secho("Generating typescript api client", fg="yellow")
    build_api_definition(env)


def build_api_definition(env: Environment) -> None:
    template = env.get_template("interface.ts")
    for rule in current_app.url_map.iter_rules():
        sig = inspect.signature(current_app.view_functions[rule.endpoint])
        _generate_typed_call(template, sig, rule)


def rule_to_typename(rule: Rule) -> str:
    return f"{''.join([p.capitalize() for p in rule.endpoint.split('_')])}Request"


def _generate_typed_call(
    template: Template, sig: inspect.Signature, rule: Rule
) -> None:
    type_name = rule_to_typename(rule)
    args = {
        name: TYPE_MAPPING.get(t.annotation, t.annotation.__name__)
        for name, t in sig.parameters.items()
    }
    generated = template.render(
        interfaces=[dict(name=type_name, attributes={"url": f"'{rule.rule}'", **args})]
    )
    path = Path.cwd() / "typescript" / "generated" / "request"
    interface_import_lookup[type_name] = path / type_name
    _write_interfaces(generated, path, type_name + ".ts")


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
        all_interface = list(iterfac)
        path = Path.cwd() / "typescript" / "generated" / "interfaces"
        path = path.joinpath(mod.replace(".", "/"))
        types = _generate_interface(template, all_interface)
        _write_interfaces(types, path)
        for interface in all_interface:
            interface_import_lookup[interface.__name__] = path / "types"


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


def _write_interfaces(data: str, path: Path, name: str = "types.ts") -> None:
    path.mkdir(parents=True, exist_ok=True)
    interface = path / name
    with (path / interface).open("w+") as file:
        file.write(data)


def _needs_import(symbol: str) -> bool:
    return symbol in interface_import_lookup.keys()


def _resolve_import(symbol: str) -> str:
    if symbol in interface_import_lookup:
        return (
            (interface_import_lookup[symbol])
            .relative_to(Path.cwd() / "typescript")
            .as_posix()
        )

    # Error


def _find_dataclass_imports(values: Sequence[object]):
    """
    Locates any atttibutes that are dataclasses and makes sure they are imported
    """
    needs_import = list(
        filter(
            _needs_import, chain(*[list(a.get("attributes").values()) for a in values])
        )
    )
    resolved_imports = list(
        sorted(
            zip(map(_resolve_import, needs_import), needs_import), key=lambda i: i[0]
        )
    )
    return {
        path: list(map(lambda i: i[1], types))
        for path, types in groupby(resolved_imports, key=lambda i: i[0])
    }
