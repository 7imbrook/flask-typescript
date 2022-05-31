# Flask-Typescript
Generate a typescript api for talking to a flask app.

## Why
I find myself writing a lot of simple react-typescript apps that don't quite meet the needs of doing graphql, but still wanting types for my projects. I decided to write a client generator off of python types to make an interface between my app. 

## The current approch
The follow wouild be the type client generated from this view
```python
@dataclass(frozen=True)
class PayloadExample:
    name: str

@dataclass(frozen=True)
class LengthResponse:
    size: int

@app.route("/post", methods=["POST"])
@client_typed
def post(payload: PayloadExample, count: int) -> LengthResponse:
    return LengthResponse(size=len(payload.name))
```
```typescript
const r = await api({
    url: '/post', // <- the type is determined here
    // function arguments are enumerated here
    payload: {
        name: "hello"
    },
    count: 4
})
// the return type would be LengthResponse here
r.size
```
The parsing/generating of params and the method type of the request will all be abstracted inside the api call. Generating a bunch of type overrides would allow for the response to be mapped
`async function api(r: PostRequest): Promise<LengthResponse>;`

## How to use
This isn't packaged yet, but the general principle is in example. It registers a flask command that will go over all the views and generate typescript. This needs more configuration to be general purpose and some things don't work yet. Separate from type generation, is enforcement, that using the type signature to parse json requests into dataclasses.

## What this is not
- Forward backward compatible
  - Going for simple, single server application for the home lab
  - Maybe a project down the line will be to route to server version in consul or something
