// Imports here
{%- for path, types in interfaces | find_dataclass_imports | dictsort %}
import { {{ types | join(", ") }} } from '{{path}}';
{%- endfor %}