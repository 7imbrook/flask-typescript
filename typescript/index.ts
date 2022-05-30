import { LengthResponse } from "generated/interfaces/example/app/types";
import { SimpleID } from "generated/interfaces/example/schema/types";
import { NumberRequest } from "generated/request/NumberRequest";
import { PostRequest } from "generated/request/PostRequest";

type APIUrl = '/post' | '/number';
type HTTPMethod = "POST" | "GET";

// Method type mapping
const API_METHOD_MAPPING: { [key in APIUrl]: HTTPMethod } = {
    '/post': "POST",
    '/number': "GET",
}

const API_BODY_PARAMS: { [key in APIUrl]: string[] } = {
    '/post': ["payload"],
    "/number": []
}


// Union of all types for generic implimentation
type APIRequest = PostRequest | NumberRequest;
type APIResponse = LengthResponse | SimpleID;

// All overrides to map requets to responses
async function api(r: PostRequest): Promise<LengthResponse>;
async function api(r: NumberRequest): Promise<SimpleID>;

// Above will be generated

async function api<T extends APIRequest, R extends APIResponse>(request: T): Promise<R> {
    const url = new URL(request.url, 'http://127.0.0.1:5000')
    let options = {
        method: API_METHOD_MAPPING[request.url],
        headers: {
            'Content-Type': 'application/json'
        },
        body: undefined
    };
    const body = {};
    const body_params = API_BODY_PARAMS[request.url]
    // Iterate over body keys
    body_params.forEach(element => {
        const b = request[element];
        if (b) {
            body[element] = b
        }
    });
    if (Object.keys(body).length > 0) {
        options = {
            ...options,
            body: JSON.stringify(body),
        }
    }

    Object.keys(request).filter(k => !['url', ...body_params].includes(k)).forEach(key => {
        url.searchParams.set(key, request[key]);
    })

    return await fetchTyped<R>(url, options);
}

async function fetchTyped<T>(uri: URL, options?: RequestInit): Promise<T | null> {
    const res = await fetch(uri.toString(), options);
    if (res.ok) {
        return await res.json() as T;
    } else {
        const error = await res.text()
        throw new Error(error);
    }
}

async function main() {
    const number = await api({
        url: '/number',
        custom_id: 15
    })
    console.log(number.id)

    const post = await api({
        url: '/post',
        payload: {
            name: "hello"
        }
    })
    console.log(post.size)
}
main()