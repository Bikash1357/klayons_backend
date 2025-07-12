import os

from backend_main.settings import EMAIL_TEMPLATES_DIR


available_templates_set = set(os.listdir(EMAIL_TEMPLATES_DIR))


def template_name_to_type(template_name):
    possible_html_file_name = template_name + ".html"
    possible_text_file_name = template_name + ".txt"

    if possible_html_file_name in available_templates_set:
        return "html"
    
    if possible_text_file_name in available_templates_set:
        return "txt"
    
    return None


def populate_template(template_file_name, template_fields):
    template_file_path = os.path.join(EMAIL_TEMPLATES_DIR, template_file_name)
    with open(template_file_path, 'r', encoding="utf-8") as f:
        template_str = f.read()

    for field_name, field_value in template_fields.items():
        variable_key = "{{ " + field_name + " }}"
        template_str = template_str.replace(variable_key, field_value)
    
    return template_str
