""" This script can be run from command line as 'python manage.py initial_admin_insert_into_db'
    and it's inserting first nedded values for some Models which can be done also in Django Admin Section,
    but here it's more automatic and quikly"""
from django.core.management.base import BaseCommand
import os
import glob
import datetime
import diary.serializers as serializers

# For using and testing all REST API endpoints - before it Admin should insert several first values to some tables in DB.
# Here is a list what should be done and with such exact values - then All examples in REST API endpoints descriptions will work.
# But if don't want to test these API examples - you don't need to make this initial insert into DB. 
# Youc can insert your own values and start using service with them.
# One more time - this script insert first values only for the reason that REST API examples will not throw errors if you try them as described in each enndpoint.

# Admin should insert these values into these tables in DB:
values_for_insert_into_db = {
    # - insert into "Entry Categories" 1 value: 
    'entry_category_first_values': {"name": "Notes"},

    # - insert into "Entry Tags" 2 values: 
    'entry_tag_first_values': [{"name": "note"}, {"name": "long-read"}],

    # - insert into "Journey Types" 1 value:
    'journey_type_first_values': {"name": "just for weekend"},

    # - insert into "Journey Countries" 2 values: 
    'journey_country_first_values': [
        {"name": "United Kingdome", "lang": "english", "flag": "🇬🇧"},
        {"name": "France", "lang": "french", "flag": "🇫🇷"},
    ],

    # - insert into "Questions groups" 1 value: 
    'questions_group_first_values': {"group_name": "Group1", "max_score": 25, "result_types": {"good": [0,13], "bad": [14,25]}},
    # with QuestionGroup also will be inserted first values for "Timeline event categories" with values: {"id": 1, "category_name": "App Achievements"} 

    # - insert into "Questions" 2 values: 
    'question_first_values': [
        {"question_text": "Is this question awesome?", "order": 1, "questions_group": 1}, # (without any choices)
        {"question_text": "Another question is better?", "order": 2, "questions_group": 1} # (without any choices)
    ],

    # - insert into "Choices" 2 values: 
    'choice_first_values': [
        {"choice_text": "Yes, it's awesome!", "order": 1, "question": [1, 2]},
        {"choice_text": "No, it's even better!", "order": 2, "question": [1, 2]}
    ],

    # - insert into "Timeline event categories" 1 value: 
    'timeline_event_category_first_values': {"category_name": "Good Events"},
    # this value will not be first, but second, because first value was inserted with QuestionGroup (above). So this value will be with id = 2

    # - insert into "Timeline event templates" 1 value: 
    'timeline_event_template_first_values': {"event": "Some Good Event", "event_category": 2},
    # in these values we set event_category = 2 because it's first meaningful EventCategory and EventCategory with id = 1 was technical "App Achievements"

    # - insert into "Timeline event reaction category" 1 value: 
    'event_reaction_category_first_values': {"category_name": "Happy reactions"}
}

class Command(BaseCommand):
    help = 'inserting first nedded values for some Models'

    def handle(self, *args, **options):
        print('START script: initial_admin_insert_into_db!')
        for model, values in values_for_insert_into_db.items():
            try:
                model_name_snake_case = model.replace('_first_values', '')
                print(f'\ninserting first values for model: {model_name_snake_case}...')
                model_name_camel_case = ''.join(x.capitalize() for x in model_name_snake_case.split('_'))

                SerializerClass = getattr(serializers, f'{model_name_camel_case}Serializer')
                if isinstance(values, list):
                    serializer = SerializerClass(data=values, many=True)
                else:
                    serializer = SerializerClass(data=values, many=False)

                if serializer.is_valid():
                    try:
                        serializer.save()
                        print(f'Successfully INSERTED first values for model: {model_name_snake_case}: Inserted data: {serializer.data}')
                    except Exception as e:
                        print(f'Error in Inserting first values for model: {model_name_snake_case}: {e}')
                else:
                    raise Exception(f'Error in Inserting first values for model: {model_name_snake_case}: incoming data is not valid: {serializer.data}. Errors: {serializer.errors}')
            except Exception as e:
                print(f'Error while inserting first values for {model_name_snake_case}: {e}')
        print('FINISH script: initial_admin_insert_into_db!')