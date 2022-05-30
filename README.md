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
