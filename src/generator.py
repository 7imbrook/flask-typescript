from dataclasses import is_dataclass
import inspect
from itertools import chain, groupby
from pathlib import Path
from subprocess import check_output
from typing import Sequence, Set
import click
from flask import current_app
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
    env.filters["resolve_imports"] = _resolve_imports
    if clean:
        click.secho("Cleaning generated files", fg="red")
        check_output(["rm", "-r", "./typescript/generated"])

    click.secho("Generating typescript interfaces for used dataclasses", fg="yellow")
    build_interfaces(env)
    click.secho("Generating typescript request types", fg="yellow")
    build_api_definition(env)
    click.secho("Generating typescript api client", fg="yellow")
    build_api_client(env)


def build_api_client(env: Environment) -> None:
    template = env.get_template("overrides.ts")
    urls = [r.rule for r in current_app.url_map.iter_rules()]
    requests = {rule_to_typename(r) for r in current_app.url_map.iter_rules()}
    responses = {rule_to_reponse(r) for r in current_app.url_map.iter_rules()}
    overrides = {
        (rule_to_typename(r), rule_to_reponse(r))
        for r in current_app.url_map.iter_rules()
    }
    method_mapping = {
        r.rule: rule_to_prefered_method(r) for r in current_app.url_map.iter_rules()
    }
    filter_body_params = {
        r.rule: rule_to_filtered_body_params(r)
        for r in current_app.url_map.iter_rules()
    }
    client_overrides = template.render(
        urls=urls,
        requests=requests,
        responses=responses,
        overrides=overrides,
        method_mapping=method_mapping,
        filter_body_params=filter_body_params,
        imports=requests.union(responses),
    )
    path = Path.cwd() / "typescript" / "generated" / "client"
    _write_file(client_overrides, path, "api.ts")
    # Populate imports if needed


def build_api_definition(env: Environment) -> None:
    template = env.get_template("interface.ts")
    for rule in current_app.url_map.iter_rules():
        sig = inspect.signature(current_app.view_functions[rule.endpoint])
        _generate_typed_call(template, sig, rule)


def rule_to_typename(rule: Rule) -> str:
    return f"{''.join([p.capitalize() for p in rule.endpoint.split('_')])}Request"


def rule_to_reponse(rule: Rule) -> str:
    return inspect.signature(
        current_app.view_functions[rule.endpoint]
    ).return_annotation.__name__


def rule_to_prefered_method(rule: Rule):
    for method in rule.methods:
        if method in ["GET", "POST", "PUT", "DELETE"]:
            return method


def rule_to_filtered_body_params(rule: Rule):
    if "GET" in rule.methods:
        # This will skip places where we have one method handle multiple types, I like to avoid this but its not enforced
        return []
    return [
        p
        for p, t in inspect.signature(
            current_app.view_functions[rule.endpoint]
        ).parameters.items()
        if is_dataclass(t.annotation)
    ]


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
    _write_file(generated, path, type_name + ".ts")


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
        _write_file(types, path, "types.ts")
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


def _write_file(data: str, path: Path, name: str) -> None:
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
    return _resolve_imports(
        chain(*[list(a.get("attributes").values()) for a in values])
    )


def _resolve_imports(classes: Sequence[str]):
    needs_import = list(filter(_needs_import, classes))
    resolved_imports = list(
        sorted(
            zip(map(_resolve_import, needs_import), needs_import), key=lambda i: i[0]
        )
    )
    return {
        path: list(map(lambda i: i[1], types))
        for path, types in groupby(resolved_imports, key=lambda i: i[0])
    }
