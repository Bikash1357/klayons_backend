def try_get_object_by_unique_field(model, field_name, value):
    try:
        model_object = model.objects.get(**{field_name: value})
    except model.DoesNotExist:
        return None
    
    return model_object


def flatten_nested_filter(nested_dict, prefix=""):
    """
    Flattens a nested dictionary into Django ORM double-underscore filters.
    E.g. {"a": {"b": {"c": 1}}} -> {"a__b__c": 1}
    """
    
    items = {}
    for key, value in nested_dict.items():
        new_key = f"{prefix}__{key}" if prefix else key
        if isinstance(value, dict):
            items.update(flatten_nested_filter(value, new_key))
        else:
            items[new_key] = value
    
    return items


def get_object_by_nested_lookup(model_class, nested_filter):
    """
    Given a Django model and a nested dictionary filter, return a single object.
    """

    flat_filter = flatten_nested_filter(nested_filter)
    return model_class.objects.get(**flat_filter)
