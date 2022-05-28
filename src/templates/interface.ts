// Generated file
// To regenereate run flask generate-typescript
{% for i in interfaces %}
export interface {{ i.name }} {
    {%- for n, t in i.attributes.items() %}
    {{n}}: {{t}};
    {%- endfor %}
}
{% endfor %}
