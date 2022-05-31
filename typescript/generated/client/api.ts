// Generated file
// To regenereate run flask generate-typescript

// Imports here
import { CustomResponse, LengthResponse, ExampleType } from 'generated/interfaces/example/app/types';
import { SimpleID } from 'generated/interfaces/example/schema/types';
import { IndexRequest } from 'generated/request/IndexRequest';
import { NamingSecondRequest } from 'generated/request/NamingSecondRequest';
import { NumberRequest } from 'generated/request/NumberRequest';
import { ParamsRequest } from 'generated/request/ParamsRequest';
import { PostRequest } from 'generated/request/PostRequest';
import { QueryRequest } from 'generated/request/QueryRequest';

export type APIUrl = "/" | "/<int:custom_id>" | "/naming" | "/number" | "/post" | "/via_query";
export type APIRequest = IndexRequest | NamingSecondRequest | NumberRequest | ParamsRequest | PostRequest | QueryRequest;
export type APIResponse = CustomResponse | ExampleType | LengthResponse | SimpleID;

type HTTPMethod = "POST" | "GET" | "PUT" | "DELETE";

// Method type mapping
const API_METHOD_MAPPING: { [key in APIUrl]: HTTPMethod } = {
    "/": "GET",
    "/<int:custom_id>": "GET",
    "/naming": "POST",
    "/number": "GET",
    "/post": "POST",
    "/via_query": "GET",
}

// Filter params that need to be in the body
const API_BODY_PARAMS: { [key in APIUrl]: string[] } = {
    "/": [],
    "/<int:custom_id>": [],
    "/naming": ["payload", "idz"],
    "/number": [],
    "/post": ["payload"],
    "/via_query": [],
}


export async function api(request: PostRequest): Promise<LengthResponse>;
export async function api(request: IndexRequest): Promise<CustomResponse>;
export async function api(request: QueryRequest): Promise<ExampleType>;
export async function api(request: ParamsRequest): Promise<CustomResponse>;
export async function api(request: NumberRequest): Promise<SimpleID>;
export async function api(request: NamingSecondRequest): Promise<ExampleType>;
export async function api<T extends APIRequest, R extends APIResponse>(request: T): Promise<R> {
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