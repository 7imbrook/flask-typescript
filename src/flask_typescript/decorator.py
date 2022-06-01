from dataclasses import asdict, is_dataclass
import functools
import inspect
from inspect import _empty
from flask import has_request_context, request, abort


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
