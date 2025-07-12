import json
import os

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_duration

from authentication.models import CustomUser, ParentUser, InstructorUser
from activities.models import (
    Child,
    ActivityCategory,
    Activity,
    ActivityInstance,
    ActivitySession,
    ActivityBooking,
)
from backend_main.utils.orm_utils import get_object_by_nested_lookup
from core.models import Society


DELETE_ALL_ALLOWED = True

dummy_data_json_path = os.path.join(os.path.dirname(__file__), "dummy_data.json")

toposorted_model_names = [
    "Society",
    "ActivityCategory",
    "SuperUser",
    "CustomUser",
    "ParentUser",
    "InstructorUser",
    "Child",
    "Activity",
    "ActivityInstance",
    "ActivitySession",
]
model_name_to_class_map = {
    'Society': Society,
    'ActivityCategory': ActivityCategory,
    'SuperUser': CustomUser,
    'CustomUser': CustomUser,
    'ParentUser': ParentUser,
    'InstructorUser': InstructorUser,
    'Child': Child,
    'Activity': Activity,
    'ActivityInstance': ActivityInstance,
    'ActivitySession': ActivitySession,
    'ActivityBooking': ActivityBooking,
}


def parse_fields(model_class, data_dict):
    """
    Parses datetime and duration fields in the data_dict based on the model_class definition.
    Converts datetimes to timezone-aware objects if USE_TZ is True.
    """
    parsed_data = data_dict.copy()

    for field in model_class._meta.get_fields():
        if isinstance(field, (models.DateTimeField, models.DurationField)):
            field_name = field.name
            raw_value = data_dict.get(field_name)
            if raw_value:
                if isinstance(field, models.DateTimeField):
                    dt = parse_datetime(raw_value)
                    if dt and timezone.is_naive(dt) and timezone.get_current_timezone():
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    parsed_data[field_name] = dt
                elif isinstance(field, models.DurationField):
                    parsed_data[field_name] = parse_duration(raw_value)

    return parsed_data


def clear_data():
    for model_name in reversed(toposorted_model_names):
        model_class = model_name_to_class_map[model_name]

        all_objects = model_class.objects.all()
        num_objects = all_objects.count()

        if num_objects > 0:
            model_name_full = model_class._meta.verbose_name or model_class.__name__
            
            if not DELETE_ALL_ALLOWED:
                print(f"  Found {num_objects} existing objects of model '{model_name_full}', cannot clear. Exiting ...")
                exit(1)

            print(f"  Found {num_objects} existing objects of model '{model_name_full}'. Deleting ...")
            for obj in all_objects:
                obj_id = obj.id
                obj.delete()
                print(f"    Deleted object with ID: {obj_id}")


def create_dummy_data():
    with open(dummy_data_json_path, 'r') as f:
        data = json.load(f)
    
    for model_name in toposorted_model_names:
        model_metadata = data['models'][model_name]
        _primary_key = model_metadata['primary_key']
        creator_function_name = model_metadata.get('creator_function', "create")

        model_class = model_name_to_class_map[model_name]
        model_creator_function = getattr(model_class.objects, creator_function_name)

        print(f"  Creating objects of {model_name}")
        model_objects_to_create = data['objects'][model_name]
        for object in model_objects_to_create:
            populated_object = {}
            many_to_many_field_values = {}
            for key, value in object.items():
                if isinstance(value, dict):
                    related_field_name = key
                    related_model_class = model_class._meta.get_field(related_field_name).related_model
                    
                    # value is the nested relation
                    resolved_value = get_object_by_nested_lookup(related_model_class, value)
                    populated_object[key] = resolved_value
                elif isinstance(value, list):
                    related_field_name = key
                    related_model_class = model_class._meta.get_field(related_field_name).related_model

                    many_to_many_field_values[key] = []
                    for related_object in value:
                        resolved_value = get_object_by_nested_lookup(related_model_class, related_object)
                        many_to_many_field_values[key].append(resolved_value)
                else:
                    populated_object[key] = value
            
            parsed_populated_object = parse_fields(model_class, populated_object)
            
            new_object = model_creator_function(**parsed_populated_object)
            print(f"    Created object with ID: {new_object.id}")
            for field_name, field_items in many_to_many_field_values.items():
                getattr(new_object, field_name).set(field_items)
        
        print("   ... done.")


def seed_dummy():
    print("Clearing previously seeded data ...")
    clear_data()
    print(" ... done.")
    print("")

    print("Seeding dummy data ...")
    create_dummy_data()
    print(" ... done.")
    print("")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        seed_dummy()
