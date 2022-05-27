// Generated file
// To regenereate run flask generate-typescript

interface {{ name }} {
    {%- for n, t in attributes.items() %}
    {{n}}: {{t}};
    {%- endfor %}
}

