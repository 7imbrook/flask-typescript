// Generated file
// To regenereate run flask generate-typescript

export default interface {{ name }} {
    {%- for n, t in attributes.items() %}
    {{n}}: {{t}};
    {%- endfor %}
}

