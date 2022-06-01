// Generated file
// To regenereate run flask generate-typescript

{% include 'import.ts' %}

{% for i in interfaces | sort(attribute='name') %}
export interface {{ i.name }} {
    {%- for n, t in i.attributes | dictsort %}
    {{n}}: {{t}};
    {%- endfor %}
}
{% endfor %}
