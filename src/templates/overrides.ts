// Generated file
// To regenereate run flask generate-typescript

{% include 'import.ts' %}

export type APIUrl = "{{ urls | sort | join('" | "') }}";
export type APIRequest = {{ requests | sort | join(" | ") }};
export type APIResponse = {{ responses | sort | join(" | ") }};

type HTTPMethod = "POST" | "GET" | "PUT" | "DELETE";

// Method type mapping
const API_METHOD_MAPPING: { [key in APIUrl]: HTTPMethod } = {
    {%- for url, method in method_mapping | dictsort %}
    "{{ url }}": "{{ method }}",
    {%- endfor %}
}

// Filter params that need to be in the body
const API_BODY_PARAMS: { [key in APIUrl]: string[] } = {
    {%- for url, params in filter_body_params | dictsort %}
    "{{ url }}": {{ params | tojson }},
    {%- endfor %}
}

{% for req, res in overrides %}
export async function api(request: {{req}}): Promise<{{res}}>;
{%- endfor %}
{%- include 'client.ts' %}
