// Generated file
// To regenereate run flask generate-typescript

{% include 'import.ts' %}

export type APIUrl = "{{ urls | sort | join('" | "') }}";
export type APIRequest = {{ requests | sort | join(" | ") }};
export type APIResponse = {{ responses | sort | join(" | ") }};