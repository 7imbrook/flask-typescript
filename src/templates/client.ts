
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