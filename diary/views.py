from rest_framework.decorators import api_view
from rest_framework.views import Response, exception_handler
from rest_framework import status as http_status
from rest_framework.exceptions import MethodNotAllowed
from django.db.models import F, Q
from diary.models import *
from .serializers import *
import copy
from datetime import datetime, timezone
import base64
from functools import wraps


EMOTIONS_DICT = {
    'good': '🙂',
    'normal': '😐',
    'bad': '🙁'
}

API_SCHEMA = {
    'all_get_apis': {
        'All Questions Groups:': {
            'func': 'get_q_groups',
            'model': QuestionsGroup,
            'serializer': QuestionsGroupSerializer,
            'description': """
                Endpont for getting ALL Questions Groups.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Groups - it will be shown as a Result below:
                If there is no one Group in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "group_name": "Group1",
                    "group_title": "Awesome group",
                    "group_description": "Awesome description",
                    "group_time_to_pass": "5 questions, ~5 minutes",
                    "group_frequency": "every week",
                    "max_score": 25,
                    "result_types": {"good": [0, 13], "bad": [14, 25]}
                },
                {
                    "id": 2,
                    "group_name": "Group2",
                    "group_title": "Another group",
                    "group_description": "Another description",
                    "group_time_to_pass": "10 questions, ~10 minutes",
                    "group_frequency": "every month",
                    "max_score": 50,
                    "result_types": {"bad": [0, 10], "normal": [11, 30], "good": [31, 50]}
                }
            ]
        },
        'All Questions:': {
            'func': 'get_questions',
            'model': Question,
            'serializer': QuestionSerializer,
            'description': """
                Endpont for getting ALL Questions.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Questions - it will be shown as a Result below:
                If there is no one Question in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "question_text": "Is this question awesome?",
                    "order": 1,
                    "questions_group": 1
                },
                {
                    "id": 2,
                    "question_text": "Maybe thi one is awesome too?",
                    "order": 2,
                    "questions_group": 1
                }
            ]
        },
        'All Choices:': {
            'func': 'get_choices',
            'model': Choice,
            'serializer': ChoiceSerializer,
            'description': """
                Endpont for getting ALL Choices (of answers) for Questions.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Choices - it will be shown as a Result below:
                If there is no one Choice in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "choice_text": "Yes, it's awesome!",
                    "order": 1,
                    "question": [1,2]
                },
                {
                    "id": 2,
                    "choice_text": "No, it's even better!",
                    "order": 2,
                    "question": [1,2]
                }
            ]
        },
        'All Questions & Choices by Question Group:': {
            'func': 'get_qc_by_q_group_name',
            'description': """
                Endpont for getting ALL Questions with their Choices (of answers) for one Question Group.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - questions_group

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 1 string value: questions_group. You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?questions_group=Group1',
            'result example': [
                {
                    "group_id": 1,
                    "data_list": [
                        {
                            "question_text": "Is this question awesome?",
                            "group_id": 1,
                            "question_id": 1,
                            "choices": [
                                {
                                    "choice_id": 1,
                                    "choice_text": "Yes, it's awesome!"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_text": "No, it's even better!"
                                }
                            ]
                        },
                        {
                            "question_text": "Maybe thi one is awesome too?",
                            "group_id": 1,
                            "question_id": 2,
                            "choices": [
                                {
                                    "choice_id": 1,
                                    "choice_text": "Yes, it's awesome!"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_text": "No, it's even better!"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        'All Users:': {
            'func': 'get_users',
            'model': DiaryUser,
            'serializer': DiaryUserSerializer,
            'description': """
                Endpont for getting ALL Diary Users (not Django Users).
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Diary Users - it will be shown as a Result below:
                If there is no one Diary User in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "some-awesome-email@test.test"
                },
                {
                    "id": 2,
                    "name": "Merry Popins",
                    "email": "another-awesome-email@test.test"
                }
            ]
        },
        'Get One User by email': {
            'func': 'get_one_user',
            'description': """
                Endpont for getting Diary User by Email.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - email

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 1 string value: email. You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?email=some-awesome-email@test.test',
            'result example': [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "some-awesome-email@test.test"
                }
            ]
        },
        'All Users Answers:': {
            'func': 'get_users_answers',
            'model': UsersAnswer,
            'serializer': UsersAnswerSerializer,
            'description': """
                Endpont for getting ALL Diary Users Answers for Questios.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Diary Users Answers - it will be shown as a Result below:
                If there is no one Diary User Answer in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "created_at": "2025-02-09T09:27:10.223088Z",
                    "user": 1,
                    "question": 1,
                    "answer": 1,
                    "user_completed_poll": 1
                },
                {
                    "id": 1,
                    "created_at": "2025-02-09T09:28:11.223088Z",
                    "user": 1,
                    "question": 2,
                    "answer": 2,
                    "user_completed_poll": 1
                },
            ]
        },
        'All Users Completed Polls:': {
            'func': 'get_users_cps',
            'model': UsersCompletedPoll,
            'serializer': UsersCompletedPollSerializer,
            'description': """
                Endpont for getting ALL Diary Users Complited Polls 
                (when User answered to all question of some Questions Group and finish th whole Poll).
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Diary Users Complited Polls - it will be shown as a Result below:
                If there is no one Diary User Complited Poll in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "completed_at": "2025-02-09T09:26:57.690978Z",
                    "user": 1,
                    "questions_group": 1
                },
                {
                    "id": 2,
                    "completed_at": "2025-02-09T10:27:01.690978Z",
                    "user": 1,
                    "questions_group": 2
                },
            ]
        },
        'Get One User Complited Poll results by Questions Group:': {
            'func': 'get_user_cp_result_by_q_group_name',
            'description': """
                Endpont for getting Diary User Complited Poll results by Questions Group.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - user_id
                - questions_group_name

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 2 values: user_id (int), questions_group_name (string). You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?user_id=1&questions_group_name=Group1',
            'result example': [
                {
                    "total_score": 15,
                    "total_cat": "good",
                    "total_prc": 55
                }
            ]
        },
        'All Journeys with Countries': {
            'func': 'get_journeys_with_countries',
            'description': """
                Endpont for getting ALL Journeys with their associated Countries (by their Flags)
                (One Journey can be associated with many Countries).
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Journeys - it will be shown as a Result below:
                If there is no one Journey in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "journey_id": 1,
                    "user_id": 1,
                    "journey_type": "just for weekend",
                    "title": "Trip to Paris & London",
                    "dates": "2018-05-01 to 2018-05-03",
                    "description": "just to taste fried frogs and pizza",
                    "link": "www.awesome-europe-trip.com",
                    "countries": ["🇫🇷", "🇬🇧"]
                },
                {
                    "journey_id": 2,
                    "user_id": 1,
                    "journey_type": "just for weekend",
                    "title": "Trip to Tokio & Pekin",
                    "dates": "2008-05-01 to 2008-05-03",
                    "description": "just to taste sushi and wok",
                    "link": "www.awesome-asia-trip.com",
                    "countries": ["🇯🇵", "🇨🇳"]
                }
            ]
        },
        'All Entries': {
            'func': 'get_entries',
            'description': """
                Endpont for getting Diary Entries for some Diary User.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - need_full_data - because the full data response contains base64 (binary) data of image and for audio
                and as plain text is too big for show it in browser (but it can be easily readed by script request).
                So if you want just to see in browser how it can looks like - set need_full_data=false as query param.
                But if you really need full data in response - set need_full_data=true as query param.
                If you didn't set this param anyway - the response will be shown cutted as if you set need_full_data=false.

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 1 values: need_full_data (bool). You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?need_full_data=false',
            'result example': [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "First Entry",
                    "date_time": "2025-02-13T20:20:56Z",
                    "description": "about starting my Diary",
                    "text": "Hello, Diary! I write you my first entry. Don't know what to write about but I like the whole process of it!",
                    "cat_name": "Notes",
                    "image_base64": "iVBORw0KGgoAAAANSUhE... (end cutted because of very long length)",
                    "audio_base64": "//uQxAAAAAAAAAAAAAAA... (end cutted because of very long length)",
                    "tags": [
                        "note"
                    ]
                },
                {
                    "id": 2,
                    "user_id": 1,
                    "title": "How I spend my summer vacations",
                    "date_time": "2025-02-13T20:24:10Z",
                    "description": "it's a long story about what we did last summer",
                    "text": "So I should tell a very long story about it. I will start from the beginning...",
                    "cat_name": "Long stories",
                    "image_base64": "AAABAA0AMDAQAAEABABo... (end cutted because of very long length)",
                    "audio_base64": "//uQxAAAAAAAAAAAAAAA... (end cutted because of very long length)",
                    "tags": [
                        "long-read",
                        "scary"
                    ]
                }
            ]
        },
        'Get Entry by id:': {
            'func': 'get_entry_by_id',
            'description': """
                Endpont for getting exact Diary Entry.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send values for:
                - entry_id - as a result will be shown data about this exact Entry
                - need_full_data - because the full data response contains base64 (binary) data of image and for audio
                and as plain text is too big for show it in browser (but it can be easily readed by script request).
                So if you want just to see in browser how it can looks like - set need_full_data=false as query param.
                But if you really need full data in response - set need_full_data=true as query param.
                If you didn't set this param anyway - the response will be shown cutted as if you set need_full_data=false.

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 2 values: entry_id (int), need_full_data (bool). You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?entry_id=1&need_full_data=false',
            'result example': {
                    "id": 1,
                    "title": "First Entry",
                    "date": "2025-02-13T20:20:56Z",
                    "description": "about starting my Diary",
                    "text": "Hello, Diary! I write you my first entry. Don't know what to write about but I like the whole process of it!",
                    "cat_name": "Notes",
                    "image_base64": "iVBORw0KGgoAAAANSUhE... (end cutted because of very long length)",
                    "audio_base64": "//uQxAAAAAAAAAAAAAAA... (end cutted because of very long length)",
                    "tags": [
                        "note"
                    ]
            }
        },
        'Get Entries by category:': {
            'func': 'get_entries_by_cat_name',
            'description': """
                Endpont for getting exact Diary Entry by Entries Category.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - need_full_data - because the full data response contains base64 (binary) data of image
                and as plain text is too big for show it in browser (but it can be easily readed by script request).
                So if you want just to see in browser how it can looks like - set need_full_data=false as query param.
                But if you really need full data in response - set need_full_data=true as query param.
                If you didn't set this param anyway - the response will be shown cutted as if you set need_full_data=false.

                Also as not required, but possible GET param you can send value for:
                - category_name - as a result will be shown Entries from this Entries Category

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 1 value: need_full_data (bool). Also GET data can contain 1 value: category_name (str). You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?category_name=Notes&need_full_data=false',
            'result example': [
                {
                    "category": "Notes",
                    "entries": [
                        {
                            "id": 1,
                            "user_id": 1,
                            "title": "First Entry",
                            "date_time": "2025-02-13T20:20:56Z",
                            "description": "about starting my Diary",
                            "text": "Hello, Diary! I write you my first entry. Don't know what to write about but I like the whole process of it!",
                            "cat_name": "Notes",
                            "image_base64": "iVBORw0KGgoAAAAN... (end cutted because of very long length)",
                            "audio_base64": "SUQzBAAAAAAAIlRT... (end cutted because of very long length)",
                            "tags": [
                                "note"
                            ]
                        }
                    ]
                },
                {
                    "category": "Long stories",
                    "entries": [
                        {
                            "id": 2,
                            "user_id": 1,
                            "title": "How I spend my summer vacations",
                            "date_time": "2025-02-13T20:24:10Z",
                            "description": "it's a long story about what we did last summer",
                            "text": "So I should tell a very long story about it. I will start from the beginning...",
                            "cat_name": "Long stories",
                            "image_base64": "iVBORw0KGgoAAAAN... (end cutted because of very long length)",
                            "audio_base64": "SUQzBAAAAAAAIlRT... (end cutted because of very long length)",
                            "tags": [
                                "long-read",
                                "scary"
                            ]
                        }
                    ]
                }
            ]
        },
        'All Timelines:': {
            'func': 'get_timelines',
            'model': UsersTimeline,
            'serializer': UsersTimelineSerializer,
            'description': """
                Endpont for getting ALL Users Timelines.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines - it will be shown as a Result below:
                If there is no one Timeline in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "start_dt": "2025-02-08T15:10:12.808766Z",
                    "description": "timeline of User1",
                    "user": 1
                },
                {
                    "id": 2,
                    "start_dt": "2025-02-08T15:10:12.808766Z",
                    "description": "timeline of User2",
                    "user": 1
                },
            ]
        },
        'All Timelines Events Categories:': {
            'func': 'get_tl_events_categories',
            'model': TimelineEventCategory,
            'serializer': TimelineEventCategorySerializer,
            'description': """
                Endpont for getting ALL Users Timelines Events Categories.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines Events Categories - it will be shown as a Result below:
                If there is no one Timelines Events Category in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "category_name": "App Achievements"
                },
                {
                    "id": 2,
                    "category_name": "Good Events"
                }
            ]
        },
        'All Timelines Events Templates:': {
            'func': 'get_tl_events_templates',
            'model': TimelineEventTemplate,
            'serializer': TimelineEventTemplateSerializer,
            'description': """
                Endpont for getting ALL Users Timelines Events Templates.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines Events Templates - it will be shown as a Result below:
                If there is no one Timelines Events Template in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "event": "Registration in App",
                    "event_category": 1
                },
                {
                    "id": 2,
                    "event": "Some Good Event",
                    "event_category": 2
                }
            ]
        },
        'All Timeline Event Categories with Templates:': {
            'func': 'get_tl_event_cats_with_templates',
            'description': """
                Endpont for getting ALL Timeline Event Categories with Templates results 
                (with default order or with order by exact 'event_id').
                Allow only GET method! 
                Does not require any GET params.
                But - if you need re-order list of All results by exact 'event_id':
                As GET param (at the end of URL, after "?" symbol) you can send value for:
                - event_id
                Then you will receive also ALL results but the Category of 'event_id' will be at the 1 place in list
                and the Template of 'event_id' will be at the 1 place in list.

                In Result there will be 2 additional fields:
                - result_ordering: describing how Categories AND Templates were ordered (by default or by provided event_id)
                - reason_of_such_ordering: describing why such ordering was choosen 
                  (if event_id was provided or not, and if its category and its template was founded in DB or not)

                If DB already contains any of Timeline Event Categories - it will be shown as a Result below:
                If there is no one Timeline Event Category in DB - you can see how is it may looks like in Result Example:
                Example of request WITHOUT any params is below and you can try it by clicking first example Link on that page:
                Example of request WITH 'event_id' params is below and you can try it by clicking second example Link on that page:
            """,
            'detail': 'GET data can be WITHOUT any params OR it can contains 1 value: event_id (int). You can try with 2 Examples - click on the first OR second link in it', 
            'example of GET URL without any params': '',
            'example of GET URL with params': f'?event_id=1',
            'result example': [
                {
                    "category_name": "App Achievements",
                    "id": 1,
                    "event_templates": [
                        "Registration in App",
                        "Passed Group1 poll"
                    ]
                },
                {
                    "category_name": "Some other Category",
                    "id": 2,
                    "event_templates": [
                        "Awesome Event",
                        "Good Event",
                        "Bad Event"
                    ]
                }
            ]
        },
        'All Timeline Events:': {
            'func': 'get_timelines_events',
            'model': UsersTimelineEvent,
            'serializer': UsersTimelineEventSerializer,
            'description': """
                Endpont for getting ALL Users Timelines Events.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines Events - it will be shown as a Result below:
                If there is no one Timelines Event in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "created_at": "2025-02-09T18:53:09Z",
                    "event": "Registration in app",
                    "link": "link to photo",
                    "description": "someone registred in your App",
                    "emotion": "😐",
                    "user": 1,
                    "timeline": 1,
                    "category": 1,
                    "event_template": 1
                },
                {
                    "id": 2,
                    "created_at": "2025-02-09T18:53:39Z",
                    "event": "Some Good Event",
                    "link": "link to photo1",
                    "description": "test2",
                    "emotion": "🙂",
                    "user": 1,
                    "timeline": 1,
                    "category": 2,
                    "event_template": 2
                }
            ]
        },
        'All Timeline Events by user_id:': {
            'func': 'get_tl_events_by_user',
            'description': """
                Endpont for getting Timeline Events for some Diary User.
                Allow only GET method! 
                As GET param (at the end of URL, after "?" symbol) you should send value for:
                - user_id

                Example of request is below and you can try it by clicking Link on that page:
                Example of possible Result is also below:
            """,
            'detail': 'GET data should contains 1 values: user_id (int). You can try with Example - click on the link in it', 
            'example of GET URL with params': f'?user_id=1',
            'result example': {
                "user_id": 1,
                "timeline_events": [
                    {
                        "id": 1,
                        "event": "Registration in app",
                        "created_at": "2025-02-09T18:53:09",
                        "description": "first reg",
                        "emotion": "😐",
                        "cat_name": "App Achievements",
                        "templ_name": "Registration in App",
                        "custom_event": ""
                    },
                    {
                        "id": 2,
                        "event": "Good Event",
                        "created_at": "2025-02-09T18:53:39",
                        "description": "awesome event",
                        "emotion": "🙂",
                        "cat_name": "Another Category",
                        "templ_name": "Good Event",
                        "custom_event": ""
                    }  
                ]
            }
        },
        'All Timelines Events Reactions Categories:': {
            'func': 'get_tl_events_reactions_categories',
            'model': EventReactionCategory,
            'serializer': EventReactionCategorySerializer,
            'description': """
                Endpont for getting ALL Users Timelines Events Reactions Categories.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines Events Reactions Categories - it will be shown as a Result below:
                If there is no one Timelines Events Reactions Category in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "category_name": "Happy reactions"
                },
                {
                    "id": 2,
                    "category_name": "Sad reactions"
                }
            ]
        },
        'All Timelines Events Reactions:': {
            'func': 'get_tl_events_reactions',
            'model': UsersTimelineEventReaction,
            'serializer': UsersTimelineEventReactionSerializer,
            'description': """
                Endpont for getting ALL Users Timelines Events Reactions.
                Allow only GET method! 
                Does not require any GET params.

                If DB already contains any of Timelines Events Reactions - it will be shown as a Result below:
                If there is no one Timelines Events Reaction in DB - you can see how is it may looks like in Result Example: 
            """,
            'result example': [
                {
                    "id": 1,
                    "created_at": "2025-02-10T13:02:48Z",
                    "reaction": "yeee",
                    "description": "I'm very happy after registration in App",
                    "emotion": "🙂",
                    "user": 1,
                    "event": 1,
                    "category": 1
                },
                {
                    "id": 2,
                    "created_at": "2025-02-10T13:03:43Z",
                    "reaction": "I have only 1 good event yet - it's so sad!",
                    "description": "oooh",
                    "emotion": "😩",
                    "user": 1,
                    "event": 2,
                    "category": 2
                }
            ]
        }
    },
    'all_post_apis': {
        'Add New User:': {
            'func': 'add_user', 
            'description': """
                Endpont for adding New DiaryUser (not Django User).
                Also for that new user will be created:
                - new Timeline for that user
                - new TimelineEvent on the Timeline for that new user 
                (event: "Registration in app" with category: "App Achievements")
                
                Allow only POST method! 
                As POST data you should send values for:
                - name (this one can be any text, even empty string)
                - email (this one will be checked in DB and does not allow duplicates)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 2 string values: name, email. You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {'name': 'John Doe', 'email': 'some-awesome-email@test.test'}
        },
        'Add User Completed Poll (when User just starts completing some QuestonsGroup):': {
            'func': 'add_user_completed_poll',
            'model': UsersCompletedPoll,
            'serializer':  UsersCompletedPollSerializer,
            'description': """
                Endpont for adding Diary User Complited Poll.
                You should add User Complited Poll not only after User answers all the Question of that QuestionsGroup,
                but when User just start to answer to the first Question and not yet complited it at all.
                Because for any User Answer you should send a 'user_completed_poll_id', 
                so it will be clear for which QuestionsGroup User wants to answer. 
                So it's more "potential User Complited Poll" or "future User Complited Poll".               
                Allow only POST method! 
                As POST data you should send values for:
                - user_id (int)
                - questions_group_id (int)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 2 integer values: user_id, questions_group_id. You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "user_id": 1,
                "questions_group_id": 1
            }
        },
        'Add User Answer for Question:': {
            'func': 'add_user_answer',
            'model': UsersAnswer,
            'serializer': UsersAnswerSerializer,
            'description': """
                Endpont for adding Diary User Answer to some Question.      
                You should add User Complited Poll BEFORE adding any User Answer.
                Because "User Complited Poll" it's not only after User answers all the Question of that QuestionsGroup,
                but when User just start to answer to the first Question and not yet complited it at all.
                Because for any User Answer you should send a 'user_completed_poll_id', 
                so it will be clear for which QuestionsGroup User wants to answer. 
                So it's more "potential User Complited Poll" or "future User Complited Poll".          
                Allow only POST method! 
                As POST data you should send values for:
                - user_id (int)
                - question_id (int)
                - choice_id (int)
                - user_completed_poll_id (int)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 4 integer values: user_id, question_id, choice_id (as answer), user_completed_poll_id. You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "user_id": 1,
                "question_id": 1,
                "choice_id": 1,
                "user_completed_poll_id": 1
            }
        },
        'Add User Answers with Completed Poll:': {
            'func': 'add_user_answers_with_cp',
            'description': """
                Endpont for adding Diary User Answer to all Questions for some QuestionsGroup 
                and also adding finished Complited Poll for that QuestionsGroup.
                After adding Completed Poll will be automaticly added:
                - Timeline Event like 'Passed {questions_group_name} poll' with Emotion 'Good' (🙂)

                Allow only POST method! 
                As POST data you should send values for:
                - completed_poll (dict with values):
                ---- user_id (int)
                ---- questions_group_id (int)
                - user_answers (list with values):
                ---- user_id (int)
                ---- question_id (int)
                ---- choice_id (int)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 1 dict (completed_poll) with 2 integer values: user_id, questions_group_id; 1 list (user_answers) with 3 integer values: user_id, question_id, choice_id (as answer). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "completed_poll": {"user_id": 1, "questions_group_id": 1},
                "user_answers": [
                    {"user_id": 1, "question_id": 1, "choice_id": 1},
                    {"user_id": 1, "question_id": 2, "choice_id": 2}
                ]
            }
        },
        'Add Journey': {
            'func': 'add_journey',
            'model': Journey,
            'serializer': JourneySerializer,
            'description': """
                Endpont for adding Diary User Journey. 
                Journey is mainly a text story with mentioning Journey Countries.                
                
                Allow only POST method! 
                As POST data you should send values for:
                - user_id (int)
                - type_id (int) - this should by already existing JourneyType id
                - title (str)
                - dates (str) - just any string describing dates of Journey in any format
                - description (str)
                - link (str)
                - countries (list of dicts) - this should be a list of dicts and each dict should have a key 'country_id' with value of already existing JourneyCountry id.
                
                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 11 values: user_id (int), type_id (int), title (str), dates (str), description (str), link (str), countries (list of dicts). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "user_id": 1,
                "type_id": 1,
                "title": "Awesome Journey",
                "dates": "summer of 2010 and also several days of September till 2010-09-03",
                "description": "a long story about great journey",
                "link": "link to photos album",
                "countries": [{"country_id": 1}, {"country_id": 2}]
            }
        },
        'Add Entry:': {
            'func': 'add_entry',
            'model': Entry,
            'serializer': EntrySerializer,
            'description': """
                Endpont for adding Diary User Entry. 
                Entry is mainly a text story or just note, but it can be suppoted with some image or audio.                
                
                Allow only POST method! 
                As POST data you should send values for:
                - date_time (str timestamp with format: '%Y-%m-%d %H:%M:%S', for example: '2025-10-30 21:22:23')
                - user_id (int)
                - category_id (int) - this should by already existing EntryCategory id
                - title (str)
                - description (str)
                - text (str)
                - image_name (str)
                - image_base64 (str) - this should be a string with base64 code of binary value of your image. 
                It will be decoded back to binary format and saved in DB in BinaryField. You can see the actual image in Admin Panel in Entries Section 
                - audio_name (str)
                - audio_base64 (str) - this should be a string with base64 code of binary value of your audio. 
                It will be decoded back to binary format and saved in DB in BinaryField. You can listen the actual audio in Admin Panel in Entries Section with simple player
                - tags (list of dicts) - this should be a list of dicts and each dict should have a key 'tag_id' with value of already existing Tag id.
                
                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 11 values: date_time (str), user_id (int), category_id (int), title (str), description (str), text (str), image_name (str), image_base64 (str), audio_name (str), audio_base64 (str), tags (list of dicts). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "date_time": "2025-10-30 21:22:23",
                "user_id": 1,
                "category_id": 1,
                "title": "Awesome Title",
                "description": "some description",
                "text": "a long story about something",
                "image_name": "awesome_photo",
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAcAAAAFCAYAAACJmvbYAAAEDmlDQ1BrQ0dDb2xvclNwYWNlR2VuZXJpY1JHQgAAOI2NVV1oHFUUPpu5syskzoPUpqaSDv41lLRsUtGE2uj+ZbNt3CyTbLRBkMns3Z1pJjPj/KRpKT4UQRDBqOCT4P9bwSchaqvtiy2itFCiBIMo+ND6R6HSFwnruTOzu5O4a73L3PnmnO9+595z7t4LkLgsW5beJQIsGq4t5dPis8fmxMQ6dMF90A190C0rjpUqlSYBG+PCv9rt7yDG3tf2t/f/Z+uuUEcBiN2F2Kw4yiLiZQD+FcWyXYAEQfvICddi+AnEO2ycIOISw7UAVxieD/Cyz5mRMohfRSwoqoz+xNuIB+cj9loEB3Pw2448NaitKSLLRck2q5pOI9O9g/t/tkXda8Tbg0+PszB9FN8DuPaXKnKW4YcQn1Xk3HSIry5ps8UQ/2W5aQnxIwBdu7yFcgrxPsRjVXu8HOh0qao30cArp9SZZxDfg3h1wTzKxu5E/LUxX5wKdX5SnAzmDx4A4OIqLbB69yMesE1pKojLjVdoNsfyiPi45hZmAn3uLWdpOtfQOaVmikEs7ovj8hFWpz7EV6mel0L9Xy23FMYlPYZenAx0yDB1/PX6dledmQjikjkXCxqMJS9WtfFCyH9XtSekEF+2dH+P4tzITduTygGfv58a5VCTH5PtXD7EFZiNyUDBhHnsFTBgE0SQIA9pfFtgo6cKGuhooeilaKH41eDs38Ip+f4At1Rq/sjr6NEwQqb/I/DQqsLvaFUjvAx+eWirddAJZnAj1DFJL0mSg/gcIpPkMBkhoyCSJ8lTZIxk0TpKDjXHliJzZPO50dR5ASNSnzeLvIvod0HG/mdkmOC0z8VKnzcQ2M/Yz2vKldduXjp9bleLu0ZWn7vWc+l0JGcaai10yNrUnXLP/8Jf59ewX+c3Wgz+B34Df+vbVrc16zTMVgp9um9bxEfzPU5kPqUtVWxhs6OiWTVW+gIfywB9uXi7CGcGW/zk98k/kmvJ95IfJn/j3uQ+4c5zn3Kfcd+AyF3gLnJfcl9xH3OfR2rUee80a+6vo7EK5mmXUdyfQlrYLTwoZIU9wsPCZEtP6BWGhAlhL3p2N6sTjRdduwbHsG9kq32sgBepc+xurLPW4T9URpYGJ3ym4+8zA05u44QjST8ZIoVtu3qE7fWmdn5LPdqvgcZz8Ww8BWJ8X3w0PhQ/wnCDGd+LvlHs8dRy6bLLDuKMaZ20tZrqisPJ5ONiCq8yKhYM5cCgKOu66Lsc0aYOtZdo5QCwezI4wm9J/v0X23mlZXOfBjj8Jzv3WrY5D+CsA9D7aMs2gGfjve8ArD6mePZSeCfEYt8CONWDw8FXTxrPqx/r9Vt4biXeANh8vV7/+/16ffMD1N8AuKD/A/8leAvFY9bLAAAAOGVYSWZNTQAqAAAACAABh2kABAAAAAEAAAAaAAAAAAACoAIABAAAAAEAAAAHoAMABAAAAAEAAAAFAAAAAIhergwAAAA7SURBVAgdY2z4z/G/mvk/Q+tfRgYYgPGZQAIwCZAgMp8JJgAWRSJA4kwgXTAFyCaA2CwwY2AKYHwQDQCreRwVQ1OzowAAAABJRU5ErkJggg==",
                "audio_name": "awesome_music",
                "audio_base64": "SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAwAAAAAAAAAAAAAAD/81jAAAAAAAAAAAAAWGluZwAAAA8AAAAGAAAHmAA9PT09PT09PT09PT09PT09bW1tbW1tbW1tbW1tbW1tbW2cnJycnJycnJycnJycnJyc3t7e3t7e3t7e3t7e3t7e3t77+/v7+/v7+/v7+/v7+/v7+/////////////////////8AAAAATGF2YzYxLjE5AAAAAAAAAAAAAAAAJARRAAAAAAAAB5jIlw2lAAAAAAAAAAAAAAD/84jEABKgAq7/QAAA1UJCBLmtiD/74nPiMPh+UD8QHChzgg7KAgGPy4Pg/1g+H/xACAIagQOeXP+XB94jP8EHZQEDn+XD8HwfB95c/4gDH4f5QEOc5QEFy8qIhWImMDVY90fAAAYlUBUYyCGrBVA81mXgxYWLAC4k4otdWGTISMN8FfAYdMoL07ZQJA0mAVH0SWyu/NoUCNFJtW9OdqpNxKgIQxBoEabSNquFSxqu+3yR4XDMswuITOSuTxBzXzmk1FTqOtZdtiS+2ltwlm3fh+kwovorUeiGcthbJ2vuVEVSyt3WQRL6+q2N+5g68vo4Pgujboy+Glq6rz9uMzTwwuE3MFNGupJqCV+S/DlOmGFAEQC0pmCMQJAU0C16bM7/85jEyE9UFtcfmckgVV3O1NPa7Lwx+w901G6kvlk5/8qUm5XP0dJjbk+cplb/zuc/dm56IVcoIf9qMEPxTwHallBbceJR6cvb3T/P9t5373JutRSic+ITluW00H2IxAcStUTrTsYtROD6Gdo4JznYaieUpi9PELXNxGnqU+UrmItLVbyWaSVyaFStPwGDAGEzKeicGlqgCLDAzQzkZEQcIREEDAOKzAQQRCCR4wLEwGYADmEgwFFx5LiiUQcnC4otAX5SKMKDCBplnYGUGWbGwQgowHFTEmGBGEKD4weJBoRJ8zwFmpQGUtQlxhM9nblgpOAoQsrbEZMCgYYcUPChCFWELzA4IECwgay0MMF+RIgEDwEBfUINrC6fV5mFPIxBL7Bt4eY2sOqdDey8vC5KDQACGfAAY2VAg6MGCJjWzIwcEMySLpNbYKz5SS82mPnUZWQjAU8ZGX/cFa6SEsSvLcpYAEMFRqz/85jE5WMkFsL/m9EgYxaBSoHDkik6QKEc6Ku6y+4nyg44D9xFr7/svb90GNUgFIlAmKvYmE+UiddDF5E0lJ6Yw/ZUBN0VVbA+amMVdKXWWQSji12+Wwt+G2Rtbl9LHnLcBlC9bbVWcKGTcypKPQZDjsP3MwVjatUrk9p5bUr1IzTQXDVh0W4Qt0WT0FHAk/DLp0sSym38fN+r0OS2Vv+ruJS13HTfR7mUXndafg/z213ZfuGF3IuXhV+IQQTjCAIERbUh6kMGeREarExj4TkxSMfAI1yejFIfMWAcmABgwjmBgqIxaCmWSA4oCxhklBBnGRMyYAKoKCiIwERLql/AcTBY0IQoiESqEjzmTBRZEKDhpACZQQmAEJicQw1OIQi5bhrJi4A00wcvS8edBUzhBEIY/xiBiEFIWBnXcB4RYXVVRXDAlURgZONAKBwCEjExIx0OMAD0OIKOF7zpKDjQW6RiJCXoRgj/87jEs3F8Fq7/nNgENEYqGERiouDEwGBJYCgaQmkI5g4gZEgmJEJiJIlarWzEHCC1IHiCAhGwSGSIGgEoKoHAQFDDTDHAMxcWBx0YSBLUMfBCwMmICBlJUmLDBIEMzAwOW8vqHs5bVTaXJCmWCoFLzDQ4tsYIBhcEEYKghb571KFIF3gYJhYDRIUumUbmdpaqWtdoIbiamriJUw4uRp19/KZx3VjDXnkbZ2i90Pp1JapuPCrIvBPRmjM3FUGEQTcLxMRcxmzYEqS7KCLOXBYFYdFoM2+7cpmG3ZdlpVpszlQ7uD5uX/MQKkxLl+tlYiuJYB9oAaLArB30XeqozdyHGbu3z2O430ii6ElB1/WJBYFVWVrZqXdgVRZnIoAmEAZmdpbBrAv27JiYutEoGwNhKMTExA6WYDolFpolCUZWaJQNgPCKHQLjiQUgBQ9UoGwKgFgAQLg+kVa/UVBqCkBUWuVFRUVFQ5FhY7WAeDoGxsM2uzLBQdA2D5w5BSLSuzSKirKu1kgpAVOJFRWoKFmXa1FVplrhmb9VVVUVFWkkVFVhhZV/5VWkkVFTSgVALGjBY7nYWWGb5VeVVfmtVVagoWphY5uVXlfZmb9VVa2Zr+BYWooWOFBWQ0FFVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVX/82jE2C7L2orXzEABVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/8xjE5wAAA0gAAAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU=",
                "tags": [{"tag_id": 1}, {"tag_id": 2}]
            }
        },
        'Add Timeline Event by user_id': {
            'func': 'add_timeline_event',
            'description': """
                Endpont for adding Diary User Timeline Event.               
                Allow only POST method! 
                As POST data you should send values for:
                - created_at (str timestamp with format: '%Y-%m-%d %H:%M:%S', for example: '2025-10-30 21:22:23')
                - user_id (int)
                - link (str)
                - event_category (str name of category)
                - event_template (str text of template)
                - event (str text of event, can be the same as event_template if you don't need to modify template in any ways)
                - emotion (str)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 7 values: created_at (str), user_id (int), link (str), event_category (str), event_template (str), event (str), emotion (str). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "created_at": "2025-10-30 21:22:23",
                "user_id": 1,
                "link": "awesome.photo.com",
                "event_category": "Good Events",
                "event_template": "Some Good Event",
                "event": "Some Good Event",
                "emotion": "🙂"
            }
        },
        'Add Timeline Event Reaction by event_id': {
            'func': 'add_tl_event_reaction',
            'model': UsersTimelineEventReaction,
            'serializer': UsersTimelineEventReactionSerializer,
            'description': """
                Endpont for adding Diary User Timeline Event Reaction.               
                Allow only POST method! 
                As POST data you should send values for:
                - created_at (str timestamp with format: '%Y-%m-%d %H:%M:%S', for example: '2025-10-30 21:22:23')
                - user_id (int)
                - event_id (int)
                - category_id (int)
                - reaction (str)
                - description (str)
                - emotion (str)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 7 values: created_at (str), user_id (int), event_id (int), category_id (int), reaction (str), description (str), emotion (str). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "created_at": "2025-10-30 21:22:23",
                "user_id": 1,
                "event_id": 1,
                "category_id": 1,
                "reaction": "yeee",
                "description": "I'm very happy after registration in App",
                "emotion": "🙂"
            }
        },
        'Edit Timeline Event by event_id': {
            'func': 'edit_timeline_event',
            'description': """
                Endpont for editing Diary User Timeline Event.               
                Allow only POST method! 
                As POST data you should send values for:
                - event_id (int) - it's should be already existed event_id in DB
                - created_at (str timestamp with format: '%Y-%m-%d %H:%M:%S', for example: '2025-10-30 21:22:23')
                - link (str)
                - event_category (str name of category)
                - event_template (str text of template)
                - event (str text of event, can be the same as event_template if you don't need to modify template in any ways)
                - emotion (str)

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 8 values: user_id (int), event_id (int), created_at (str), link (str), event_category (str), event_template (str), event (str), emotion (str). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "event_id": 1,
                "created_at": "2025-10-30 21:22:23",
                "link": "better.photo.com",
                "event_category": "Good Events",
                "event_template": "Some Good Event",
                "event": "Not just Good Event, but Awesome Event",
                "emotion": "🙂"
            }
        },
        'Delete Timeline Event by user_id': {
            'func': 'delete_timeline_event',
            'description': """
                Endpont for deleting Diary User Timeline Event.               
                Allow only POST method! 
                As POST data you should send values for:
                - email (str) - it's should be already existed email of User in DB whom Event you want to delete
                - name (str) - it's should be already existed name of User in DB whom Event you want to delete
                - event_id (int) - it's should be already existed event_id of that exact User (email/name) in DB which you want to delete

                Example is below and you can try it with form on that page: 
            """,
            'detail': 'POST data should contains 3 values: email (str), name (str), event_id (int). You can try with Example - copy this JSON to the form below and click "POST" button', 
            'example of POST data': {
                "email": "some-awesome-email@test.test",
                "name": "John Doe",
                "event_id": 1
            }
        }
    }
}


def func_name_defining(func):
    @wraps(func)
    def func_with_name(*args, **kwargs):
        # for use common_get_func for similar endpoints we need to now func_name to grab needed Model and Serializer from API dict by its name
        kwargs['this_func_name'] = func.__name__
        return func(*args, **kwargs)
    return func_with_name


def docstring_setup():
    def set_docstring(func):
        # where defining functions for endpoints it looks to API dict 
        # and set function docstring (description on REST page of endpoint) from API dict by the function name and type of endpoint
        if 'get' in func.__name__:
            func.__doc__ = next((v.get('description') for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == func.__name__), '')
        else:
            func.__doc__ = next((v.get('description') for k,v in API_SCHEMA['all_post_apis'].items() if v['func'] == func.__name__), '')
        return func
    return set_docstring


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add detailed description how to send proper POST request with example into response.
    if response is not None:
        if isinstance(exc, MethodNotAllowed):
            endpoint = next((v for k,v in API_SCHEMA['all_post_apis'].items() if v['func'] == context['request'].path[1:-1]), {})
            response.data['detail'] = endpoint.get('detail')
            response.data['example of POST data'] = endpoint.get('example of POST data') 
            response.status_code = 200

    return response


##################################### GET API finctions #####################################
def common_get_func(func_name):
    try:
        endpoint_info = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == func_name), '')
        data = endpoint_info.get('model').objects.all()
        serializer = endpoint_info.get('serializer')(data, many=True)
        if serializer.data:
            res =  {'res': 'good', 'data': serializer.data}
        else:
            res =  {'result example': endpoint_info.get('result example')}
        status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
def get_all_apis(request):
    try:
        base_url = request.build_absolute_uri()
        apis = copy.deepcopy(API_SCHEMA)
        for item in apis:
            for key in apis[item]:
                apis[item][key] = f'{base_url}{apis[item][key]['func']}'
        all_get_apis = apis['all_get_apis']
        all_post_apis = apis['all_post_apis']
        res = {
            'ADMIN Section': f'{base_url}admin',
            'APIs GET:': all_get_apis,
            'APIs POST:': all_post_apis
        }
        status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_q_groups(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_questions(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_choices(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
def get_qc_by_q_group_name(request):
    try:
        questions_group = request.GET.get('questions_group', '')
        if not questions_group:
            base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
            endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_qc_by_q_group_name'), {})
            res = {'detail': endpoint_dict.get('detail'),
                'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                'result example': endpoint_dict.get('result example')}
            status=http_status.HTTP_200_OK
        else:
            data = Choice.objects.prefetch_related('question').prefetch_related('questions_group')\
                .filter(question__questions_group__group_name=questions_group).all().order_by('question__id', 'order')\
                .values(
                    group_id=F('question__questions_group__id'),
                    group_name=F('question__questions_group__group_name'),
                    question_id=F('question__id'),
                    question_text=F('question__question_text'),
                    ch_id=F('id'),
                    ch_text=F('choice_text'))
            if data:
                group_id = data[0].get('group_id')
                res_dict = {}
                for item in data:
                    if item['question_text'] in res_dict:
                        res_dict[item['question_text']]['choices'].append({'choice_id': item['ch_id'],
                                                                        'choice_text': item['ch_text']})
                    else:
                        res_dict[item['question_text']] = {'group_id': item['group_id'], 
                                                        'question_id': item['question_id'], 
                                                        'choices':[{'choice_id': item['ch_id'],
                                                                        'choice_text': item['ch_text']},]}
                res_list = []
                for key in res_dict:
                    res_list.append({'question_text': key, 
                                    'group_id': res_dict[key]['group_id'],
                                    'question_id': res_dict[key]['question_id'],
                                    'choices': res_dict[key]['choices']})

                res = {'res': 'good', 'data': {'group_id': group_id, 'data_list': res_list}}
                status=http_status.HTTP_200_OK
            else:
                res = {'res': 'error', 'data': {'error': f'not found questions for this group ({questions_group})'}}
                status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST
    
    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_users(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
def get_one_user(request):
    try:
        inc_email = request.GET.get('email', '')
        if not inc_email:
            base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
            endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_one_user'), {})
            res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
            status=http_status.HTTP_200_OK
        else:
            user = DiaryUser.objects.filter(email=inc_email.lower()).first()
            if user:
                serializer = DiaryUserSerializer(user)
                res = {'res': 'good', 'data': serializer.data}
                timeline = UsersTimeline.objects.filter(user__id=res['data']['id']).first()
                if timeline:
                    res['data']['timeline_id'] = timeline.pk
                status=http_status.HTTP_200_OK
            else:
                res = {'res': 'error', 'data': {'error': f'user with such email ({inc_email}) is not founded in DB'}}
                status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_users_answers(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_users_cps(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
def get_user_cp_result_by_q_group_name(request):
    try:
        user_id = request.GET.get('user_id', '')
        questions_group_name = request.GET.get('questions_group_name', '')

        if not user_id or not questions_group_name:
            base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
            endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_user_cp_result_by_q_group_name'), {})
            res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
            status=http_status.HTTP_200_OK
        else:
            last_cp = UsersCompletedPoll.objects.filter(user__id=user_id, questions_group__group_name=questions_group_name).order_by('completed_at').last()

            if last_cp:
                data = UsersAnswer.objects.filter(user_completed_poll__id=last_cp.pk).all()\
                    .values(
                        user_name=F('user__name'),
                        user_cp_created_at=F('user_completed_poll__completed_at'),
                        question_text=F('question__question_text'),
                        question_order=F('question__order'),
                        answer_text=F('answer__choice_text'),
                        answer_order=F('answer__order')
                )

                if data:
                    try:
                        for item in data:
                            item['answer_score'] = item['answer_order'] - 1
                        total_score = sum(x['answer_score'] for x in data)
                        questions_group = QuestionsGroup.objects.filter(group_name=questions_group_name).first()
                        total_cat = 'Unknown'
                        for res_type, range_values in questions_group.result_types.items():
                            if total_score >= range_values[0] and total_score <= range_values[1]:
                                total_cat = res_type
                        total_prc = 100.0*total_score/questions_group.max_score
                        res = {'res': 'good', 'data': {'total_score': round(total_score), 'total_cat': total_cat, 'total_prc': round(total_prc)}}
                        status = http_status.HTTP_200_OK
                    except Exception as calc_e:
                        res = {'res': 'error', 'data': {'error': f'can not calc results by scores for this user: {user_id} for this ComplitedPoll: {last_cp.pk}. Error: {calc_e}'}}
                        status = http_status.HTTP_400_BAD_REQUEST
                else:
                    res = {'res': 'error', 'data': {'error': f'not found answers for this user: {user_id} for this ComplitedPoll: {last_cp.pk}'}}
                    status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'res': 'error', 'data': {'error': f'not found last ComplitedPoll for this user: {user_id} and Questions Group: {questions_group_name}'}}
                status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
def get_journeys_with_countries(*args, **kwargs):
    try:
        results_fields = ['journey_id', 'user_id', 'journey_type', 'title', 'dates', 'description', 'link']
        data = Journey.objects.all().order_by('id').annotate(journey_id=F('id'), journey_type=F('type__name')).values(*results_fields)
        res_list = [{key: d[key] for key in results_fields} for d in data]

        if res_list:
            for item in res_list:
                item['countries'] = list(Journey.objects.get(pk=item['journey_id']).country.all().values_list('flag', flat=True))
            
            res = {'res': 'good', 'data_list': res_list}
            status=http_status.HTTP_200_OK
        else:
            res =  {'result example': next((v.get('result example') for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_journeys_with_countries'), '')}
            status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
def get_entries(request):
    try:
        data = Entry.objects.all().values('id', 'user_id', 'title', 'date_time', 'description', 'text', 'image', 'audio', 
                                          cat_name=F('category__name'))
        if data:
            for item in data:
                item['image_base64'] = base64.b64encode(item['image']).decode()
                item['audio_base64'] = base64.b64encode(item['audio']).decode()
                item.pop('image')
                item.pop('audio')
                item['tags'] = list(Entry.objects.get(pk=item['id']).tag.all().values_list('name', flat=True))

            need_full_data = request.GET.get('need_full_data', False)
            if not need_full_data:
                base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
                endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_entries'), {})
                res = {'detail': endpoint_dict.get('detail'),
                       'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                       'result example': endpoint_dict.get('result example')}
            elif need_full_data and str(need_full_data).lower() == 'true':
                res = {'res': 'good', 'data': data}
            else:
                for item in data:
                    item['image_base64'] = f'{item['image_base64'][:20]}... (end cutted because of very long length)'
                    item['audio_base64'] = f'{item['audio_base64'][:20]}... (end cutted because of very long length)'
                res = {'res': 'good', 'data': data}
            status=http_status.HTTP_200_OK
        else:
            res =  {'result example': next((v.get('result example') for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_entries'), '')}
            status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
def get_entry_by_id(request):
    try:
        entry_id = request.GET.get('entry_id', '')
        if not entry_id:
            base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
            endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_entry_by_id'), {})
            res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
            status=http_status.HTTP_200_OK
        else:
            last_m = Entry.objects.filter(pk=entry_id).last()

            if last_m:
                tags = list(Entry.objects.get(pk=last_m.pk).tag.all().values_list('name', flat=True))
                category = Entry.objects.get(pk=last_m.pk).category

                data =  {
                    'id': last_m.pk, 
                    'title': last_m.title,
                    'date': last_m.date_time,
                    'description': last_m.description,
                    'text': last_m.text,
                    'cat_name': category.name,
                    'image_base64': base64.b64encode(last_m.image).decode(),
                    'audio_base64': base64.b64encode(last_m.audio).decode(),
                    'tags': tags
                }
                need_full_data = request.GET.get('need_full_data', False)
                if not need_full_data:
                    base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
                    endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_entry_by_id'), {})
                    res = {'detail': endpoint_dict.get('detail'),
                        'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                        'result example': endpoint_dict.get('result example')}
                elif need_full_data and str(need_full_data).lower() == 'true':
                    res = {'res': 'good', 'data': data}
                else:
                    data['image_base64'] = f'{data['image_base64'][:20]}... (end cutted because of very long length)'
                    data['audio_base64'] = f'{data['audio_base64'][:20]}... (end cutted because of very long length)'
                    res = {'res': 'good', 'data': data}
                status=http_status.HTTP_200_OK
            else:
                res = {'res': 'error', 'data': {'error': f'not found any Entry with this id: {entry_id}'}}
                status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
def get_entries_by_cat_name(request):
    try:
        category_name = request.GET.get('category_name', '')
        if category_name:
            data = Entry.objects.filter(category__name=category_name).all().values('id', 'user_id', 'title', 'date_time', 'description', 'text', 'image', 'audio',
                                                                                   cat_name=F('category__name'))
        else:
            data = Entry.objects.all().values('id', 'user_id', 'title', 'date_time', 'description', 'text', 'image', 'audio',
                                              cat_name=F('category__name'))
        data_list = []
        if data:
            for item in data:
                item['image_base64'] = base64.b64encode(item['image']).decode()
                item.pop('image')
                item['audio_base64'] = base64.b64encode(item['audio']).decode()
                item.pop('audio')
                item['tags'] = list(Entry.objects.get(pk=item['id']).tag.all().values_list('name', flat=True))

                cat_dict = next((d for d in data_list if d["category"] == item['cat_name']), None)
                if cat_dict:
                    cat_dict['entries'].append(item)
                else:
                    data_list.append({'category': item['cat_name'], 'entries': [item]})
            
            need_full_data = request.GET.get('need_full_data', False)
            if not need_full_data:
                base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
                endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_entries_by_cat_name'), {})
                res = {'detail': endpoint_dict.get('detail'),
                       'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                       'result example': endpoint_dict.get('result example')}
            elif need_full_data and str(need_full_data).lower() == 'true':
                res = {'res': 'good', 'data': data_list}
            else:
                for item in data_list:
                    for entry in item['entries']:
                        entry['image_base64'] = f'{entry['image_base64'][:20]}... (end cutted because of very long length)'
                        entry['audio_base64'] = f'{entry['audio_base64'][:20]}... (end cutted because of very long length)'
                res = {'res': 'good', 'data': data_list}
            status=http_status.HTTP_200_OK
        else:
            if category_name:
                res = {'res': 'error', 'data': {'error': f'not found any Entries for this Category: {category_name}'}}
                status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
                status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_timelines(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))



@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_tl_events_categories(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))



@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_tl_events_templates(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
def get_tl_event_cats_with_templates(request):
    try:
        endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_tl_event_cats_with_templates'), {})
        base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
        
        # Here we collect all Timeline Event Categories with all their possible Templates.
        # It's for example for default population dropdown lists in two Menus in some App
        # (for choosing Event Category and then choosing Template within this Category) 
        data = TimelineEventTemplate.objects.all().values('event',  
                                                        cat_id=F('event_category__id'), 
                                                        cat_name=F('event_category__category_name'))
        if data:
            res = {'res': 'good',
                   'detail': endpoint_dict.get('detail'),
                   'example of GET URL without any params': f"{base_url}{endpoint_dict.get('example of GET URL without any params')}",
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}"}
            cats_l = []
            cats_d = {}
            
            for item in data:
                if item['cat_name'] in cats_d:
                    cats_d[item['cat_name']]['event_templates'].append(item['event'])
                else:
                    cats_d[item['cat_name']] = {'id': item['cat_id'],
                                                    'event_templates':[item['event'],]}
            for key in cats_d:
                cats_l.append({'category_name': key, 
                            'id': cats_d[key]['id'],
                            'event_templates': cats_d[key]['event_templates']})
            
            # Here we also collect all Timeline Event Categories with all their possible Templates.
            # But here we have 'event_id' as a incoming param from request. 
            # And it's for the case when user want to Edit his Event in some App.
            # So then we need to re-order all Timeline Event Categories and put 'event_id' Category on the 1 place.
            # And then - when user goes to Editing his Event - 
            # in the dropdown list of Category will be choosen (at fisrt place) the Category of that exact 'event_id'.
            # So for Templates schema is the same - we should re-order Templates of that Category, 
            # and put at fisrt place - Template of that exact 'event_id'. 
            # Then in second dropdown list of Templates will be choosen the right Template in some Menu.
            event_id = request.GET.get('event_id', '')
            if event_id:
                needed_event = UsersTimelineEvent.objects.filter(pk=event_id).values(cat_name=F('category__category_name'),
                                                                                     event_cat_name=F('event_template__event')
                                                                                     ).first()
                if needed_event:
                    cat_index = next((index for (index, d) in enumerate(cats_l) 
                                    if d["category_name"] == needed_event['cat_name']), None)
                    if cat_index is not None:
                        cats_l.insert(0, cats_l.pop(cat_index)) # here we put 'event_id' Category at the 1 place and delete it from other place in list 
                        res['result_ordering'] = f'categories were ordered by provided event_id ({event_id})'
                        res['reason_of_such_ordering'] = 'event_id was provided and its category was founded in DB'
                        if needed_event['event_cat_name'] in cats_l[0]['event_templates']:
                            template_index = cats_l[0]['event_templates'].index(needed_event['event_cat_name'])
                            cats_l[0]['event_templates'].insert(0, cats_l[0]['event_templates'].pop(template_index)) # here we put 'event_id' Template at the 1 place and delete it from other place in list 
                            res['result_ordering'] = f'categories AND templates were ordered by provided event_id ({event_id})'
                            res['reason_of_such_ordering'] = 'event_id was provided and its category and its template was founded in DB'
                        else:
                            res['result_ordering'] = f'categories were ordered by provided event_id ({event_id})'
                            res['reason_of_such_ordering'] = 'event_id was provided and its category was founded in DB but its template was NOT founded in DB'
                    else:
                        res['result_ordering'] = 'default'
                        res['reason_of_such_ordering'] = 'event_id was provided but its category was NOT founded in DB'
                else:
                    res['result_ordering'] = 'default'
                    res['reason_of_such_ordering'] = f'such event_id ({event_id}) was not found in DB'
            else:
                res['result_ordering'] = 'default'
                res['reason_of_such_ordering'] = 'event_id was not provided'
            res['data'] = cats_l
        else:
            res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL without any params': f"{base_url}{endpoint_dict.get('example of GET URL without any params')}",
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
        status=http_status.HTTP_200_OK
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_timelines_events(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
def get_tl_events_by_user(request):
    try:
        user_id = request.GET.get('user_id', '')
        if not user_id:
            base_url = request.build_absolute_uri()[:request.build_absolute_uri().find('?')]
            endpoint_dict = next((v for k,v in API_SCHEMA['all_get_apis'].items() if v['func'] == 'get_tl_events_by_user'), {})
            res = {'detail': endpoint_dict.get('detail'),
                   'example of GET URL with params': f"{base_url}{endpoint_dict.get('example of GET URL with params')}",
                   'result example': endpoint_dict.get('result example')}
            status=http_status.HTTP_200_OK
        else:
            last_tl = UsersTimeline.objects.filter(user__id=user_id).order_by('start_dt').last()

            if last_tl:
                data = UsersTimelineEvent.objects.filter(timeline__id=last_tl.pk).order_by('-created_at').all()\
                                                 .values('id', 'event', 'created_at', 'description', 'emotion', 
                                                         cat_name=F('category__category_name'),
                                                         templ_name=F('event_template__event'))

                if data:
                    for event in data:
                        event['created_at'] = datetime.strftime(event['created_at'],'%Y-%m-%dT%H:%M:%S')
                        event['custom_event'] = event['event'] if event['templ_name'] == 'Custom' else ''
                    res = {'res': 'good', 'data': {'user_id': last_tl.user.pk, 'timeline_events': data}}
                    status=http_status.HTTP_200_OK
                else:
                    res = {'res': 'error', 'data': {'error': f'not found any Timeline Event for this user: {user_id} and his Timeline: {last_tl.pk}'}}
                    status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'res': 'error', 'data': {'error': f'not found any Timeline for this user: {user_id}'}}
                status=http_status.HTTP_400_BAD_REQUEST

    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_tl_events_reactions_categories(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


@api_view(['GET'])
@docstring_setup()
@func_name_defining
def get_tl_events_reactions(*args, **kwargs):
    return common_get_func(kwargs.get('this_func_name'))


##################################### POST API finctions #####################################
def common_add_func(func_name, req_data):
    try:
        endpoint_info = next((v for k,v in API_SCHEMA['all_post_apis'].items() if v['func'] == func_name), '')
        if req_data:
            data_dict = {}
            for key, value in req_data.items():
                if key == 'choice_id':
                    data_dict['answer'] = value
                elif 'id' in key:
                    data_dict[key.replace('_id', '')] = value
                elif key in ['date_time', 'created_at']:
                    data_dict[key] = datetime.strptime(value[:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                elif 'base64' in key:
                    base64_bytes_str = value.encode('utf-8')
                    decoded_binary_data = base64.decodebytes(base64_bytes_str)
                    data_dict[key.replace('_base64', '')] = decoded_binary_data
                elif key == 'tags':
                    data_dict['tag'] = [x['tag_id'] for x in value]
                elif key == 'countries':
                    data_dict['country'] = [x['country_id'] for x in value]
                else:
                    data_dict[key] = value
            serializer = endpoint_info.get('serializer')(data=data_dict)
            if serializer.is_valid():
                try:
                    serializer.save()
                    res = {'res': 'good', 'data': {'new_saved_data': serializer.data}}
                    status=http_status.HTTP_200_OK
                except Exception as e:
                    err = f"Error in Saving {endpoint_info.get('model').__name__}: {e}"
                    res = {'res': 'error', 'data': {'error': err}}
                    status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'res': 'error', 'data': {'error': f"incoming {endpoint_info.get('model').__name__} data is not valid: {serializer.data}. Errors: {serializer.errors}"}}
                status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': f"incoming {endpoint_info.get('model').__name__} data is Empty: {req_data}"}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['POST'])
@docstring_setup()
def add_user(request):
    try:
        nu_serializer = DiaryUserSerializer(data=request.data)
        nu_res = False
        if nu_serializer.is_valid():
            is_exist = DiaryUser.objects.filter(email=nu_serializer.validated_data['email']).count()

            if is_exist > 0:
                res = {'res': 'error', 'data': {'error': f"this email ({nu_serializer.validated_data['email']}) already exist"}}
                status=http_status.HTTP_400_BAD_REQUEST
            else:
                if nu_serializer.validated_data.get('email') and nu_serializer.validated_data.get('email') != '':
                    try:
                        nu_serializer.save()
                        nu_res = True
                    except Exception as e:
                        err = f'Error in Saving user: {e}'
                        res = {'res': 'error', 'data': {'error': err}}
                        status=http_status.HTTP_400_BAD_REQUEST

                    if nu_res:
                        nu_id = nu_serializer.data['id']
                        user_tl = {'user': nu_id}
                        tl_bad_res = None
                        tl_good_id = None
                        tl_event_bad_res = None
                        tl_event_good_id = None

                        tl_serializer = UsersTimelineSerializer(data=user_tl)
                        if tl_serializer.is_valid():
                            try:
                                tl_serializer.save()
                                tl_good_id = tl_serializer.data['id']
                                tech_tl_event_cat = TimelineEventCategory.objects.filter(category_name=TECHNICAL_TL_CATEGORY).first()
                                if not tech_tl_event_cat:
                                    tech_tl_event_cat = TimelineEventCategory(category_name=TECHNICAL_TL_CATEGORY)
                                    tech_tl_event_cat.save()
                                tech_tl_event_templ = TimelineEventTemplate.objects.filter(event_category=tech_tl_event_cat, event=TECH_TL_REG_NU_EVENT_TEMPLATE).first()
                                if not tech_tl_event_templ:
                                    tech_tl_event_templ = TimelineEventTemplate(event_category=tech_tl_event_cat, event=TECH_TL_REG_NU_EVENT_TEMPLATE)
                                    tech_tl_event_templ.save()
                                created_at = datetime.now().replace(tzinfo=timezone.utc) 
                                user_tl_event = {'user': nu_id, 'timeline': tl_good_id, 'category': tech_tl_event_cat.pk, 
                                                'event': TECH_TL_REG_NU_EVENT_TEMPLATE, 'emotion': EMOTIONS_DICT['good'], 
                                                'event_template': tech_tl_event_templ.pk, 'created_at': created_at}
                                tl_event_serializer = UsersTimelineEventSerializer(data=user_tl_event)
                                if tl_event_serializer.is_valid():
                                    try:
                                        tl_event_serializer.save()
                                        tl_event_good_id = tl_event_serializer.data['id']
                                    except Exception as e:
                                        err = f'Error in Saving user_timeline_event: {user_tl_event}. Error: {e}'
                                        tl_event_res = {'res': 'error', 'data': {'error': err}}
                                        tl_event_bad_res = tl_event_res
                                else:
                                    tl_event_res = {'res': 'error', 'data': {'error': f'incoming UsersTimelineEvent data is not valid: {tl_event_serializer.data}. Errors: {tl_event_serializer.errors}'}}
                                    tl_event_bad_res = tl_event_res
                            except Exception as e:
                                err = f'Error in Saving user_timeline: {user_tl}. Error: {e}'
                                tl_res = {'res': 'error', 'data': {'error': err}}
                                tl_bad_res = tl_res
                        else:
                            tl_res = {'res': 'error', 'data': {'error': f'incoming UsersTimeline data is not valid: {tl_serializer.data}. Errors: {tl_serializer.errors}'}}
                            tl_bad_res = tl_res
                        
                        if tl_bad_res or tl_event_bad_res:
                            err = f'Error in validation or saving One of UsersTimeline or UsersTimelineEvent: {tl_bad_res} / {tl_event_bad_res}'
                            res = {'res': 'error', 'data': {'error': err}}
                            status=http_status.HTTP_400_BAD_REQUEST
                        else:
                            res = {'res': 'good', 'data': {'new_user_saved_id': nu_id, 'new_user_timeline_saved_id': tl_good_id, 
                                                           'new_user_timeline_event_saved_id': tl_event_good_id}}
                            status=http_status.HTTP_200_OK
                    else:
                        res = {'res': 'error', 'data': {'error': 'new User is not saved'}}
                        status=http_status.HTTP_400_BAD_REQUEST
                else:
                    res = {'res': 'error', 'data': {'error': 'password is empty!'}}
                    status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': f'incoming DiaryUser data is not valid: {nu_serializer.data}. Errors: {nu_serializer.errors}'}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['POST'])
@docstring_setup()
@func_name_defining
def add_user_answer(*args, **kwargs):
    return common_add_func(func_name=kwargs.get('this_func_name'), req_data=args[0].data)


@api_view(['POST'])
@docstring_setup()
@func_name_defining
def add_user_completed_poll(*args, **kwargs):
    return common_add_func(func_name=kwargs.get('this_func_name'), req_data=args[0].data)


@api_view(['POST'])
@docstring_setup()
def add_user_answers_with_cp(request):
    try:
        data = request.data
        cp_res = False

        cp_data_dict = {}
        if isinstance(data, dict) and 'completed_poll' in data and isinstance(data['completed_poll'], dict) and data['completed_poll'] \
            and 'user_answers' in data and isinstance(data['user_answers'], list) and data['user_answers']: 
            for key, value in data['completed_poll'].items():
                if key in ['user_id', 'questions_group_id']:
                    cp_data_dict[key.replace('_id', '')] = value
                else:
                    cp_data_dict[key] = value

            cp_serializer = UsersCompletedPollSerializer(data=cp_data_dict)
            
            if cp_serializer.is_valid():
                try:
                    cp_serializer.save()
                    q_group = QuestionsGroup.objects.filter(pk=data['completed_poll']['questions_group_id']).first()
                    if q_group:
                        user = DiaryUser.objects.filter(pk=data['completed_poll']['user_id']).first()
                        if user:
                            timeline = UsersTimeline.objects.filter(user=user).first()
                            if timeline:
                                tl_event_cat = TimelineEventCategory.objects.filter(category_name=TECHNICAL_TL_CATEGORY).first()
                                tl_event = TECH_TL_QG_PASSED_EVENT_TEMPLATE.format(questions_group_name=q_group.group_name)
                                tl_event_template = TimelineEventTemplate.objects.filter(event_category=tl_event_cat, event=tl_event).first()
                                if not tl_event_cat or not tl_event or not tl_event_template:
                                    err = f'Not found Timeline Event Category or Timeline Event Template for adding auto-event "QuestionsGroup PASSED": tl_event_cat: {tl_event_cat}, tl_event: {tl_event}, tl_event_template: {tl_event_template}'
                                else:
                                    created_at = datetime.now()
                                    created_at = created_at.replace(tzinfo=timezone.utc)

                                    m = UsersTimelineEvent(user=user, timeline=timeline, category=tl_event_cat, event=tl_event, 
                                                        emotion=EMOTIONS_DICT['good'], event_template=tl_event_template, created_at=created_at)
                                    m.save()
                                    cp_res = True
                            else:
                                err = f"Not found Timeline for such DiaryUser: {user}"
                        else:
                            err = f"Not found such DiaryUser for user_id: {data['cp']['user_id']}"
                    else:
                        err = f"Not found such QuestionsGroup for questions_group_id: {data['cp']['questions_group_id']}"
                except Exception as e:
                    err = f'Error in add_user_answers_with_cp: in Saving user_completed_poll: {e}'

                if cp_res:
                    cp_id = cp_serializer.data['id']
                    user_answers = data['user_answers']
                    answers_bad_res = []
                    answrs_good_ids = []

                    for ans in user_answers:
                        ans['user_completed_poll'] = cp_id
                        ans_data_dict = {}
                        for key, value in ans.items():
                            if key in ['user_id', 'question_id', 'user_completed_poll_id']:
                                ans_data_dict[key.replace('_id', '')] = value
                            elif key == 'choice_id':
                                ans_data_dict['answer'] = value
                            else:
                                ans_data_dict[key] = value
                        
                        user_ans_serializer = UsersAnswerSerializer(data=ans_data_dict)

                        if user_ans_serializer.is_valid():
                            try:
                                user_ans_serializer.save()
                                answrs_good_ids.append(user_ans_serializer.data['id'])
                            except Exception as e:
                                err = f'Error in add_user_answers_with_cp: in Saving user_answer: {ans}. Error: {e}'
                                ans_res = {'res': 'error', 'data': {'error': err}}
                                answers_bad_res.append(ans_res)
                        else:
                            ans_res = {'res': 'error', 'data': {'error': f'incoming UsersAnswer data is not valid: {user_ans_serializer.data}. Errors: {user_ans_serializer.errors}'}}
                            answers_bad_res.append(ans_res)
                    if answers_bad_res:
                        err = f'Error in add_user_answers_with_cp: in validation or saving One of UsersAnswer: {answers_bad_res}'
                        res = {'res': 'error', 'data': {'error': err}}
                        status=http_status.HTTP_400_BAD_REQUEST
                    else:
                        res = {'res': 'good', 'data': {'cp_saved_id': cp_id, 'ans_saved_ids': answrs_good_ids}}
                        status=http_status.HTTP_200_OK
                else:
                    res = {'res': 'error', 'data': {'error': f'cp UserCompletedPoll is not saved! Error: {err}'}}
                    status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'res': 'error', 'data': {'error': f'incoming UserCompletedPoll data is not valid: {cp_serializer.data}. Errors: {cp_serializer.errors}'}}
                status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': f'incoming data is not valid: {data}.'}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['POST'])
@docstring_setup()
@func_name_defining
def add_entry(*args, **kwargs):
    return common_add_func(func_name=kwargs.get('this_func_name'), req_data=args[0].data)


@api_view(['POST'])
@docstring_setup()
@func_name_defining
def add_journey(*args, **kwargs):
    return common_add_func(func_name=kwargs.get('this_func_name'), req_data=args[0].data)


@api_view(['POST'])
@docstring_setup()
def add_timeline_event(request):
    try:
        data = request.data
        user = False
        timeline = False
        category = False
        event_template = False

        created_at = datetime.strptime(data['created_at'][:19], '%Y-%m-%d %H:%M:%S') 
        created_at = created_at.replace(tzinfo=timezone.utc)

        user_id = data['user_id']
        link = data['link']
        cat = data['event_category']
        event_tmpl = data['event_template']
        event = data['event']
        emotion = data['emotion']

        user = DiaryUser.objects.filter(pk=user_id).first()
        timeline = UsersTimeline.objects.filter(user__id=user_id).first()
        category = TimelineEventCategory.objects.filter(category_name=cat).first()
        event_template = TimelineEventTemplate.objects.filter(event_category=category, event=event_tmpl).first()

        if user and timeline and category and event and emotion and event_template:
            try:
                m = UsersTimelineEvent(user=user, timeline=timeline, category=category, event=event, link=link,
                                       emotion=emotion, event_template=event_template, created_at=created_at)
                m.save()
                res = {'res': 'good', 'data': {'event_saved_id': m.pk}}
                status=http_status.HTTP_200_OK
            except Exception as e:
                err = f'Error in Saving timeline_event: {e}'
                res = {'res': 'error', 'data': {'error': err}}
                status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': 'incoming data is not valid'}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['POST'])
@docstring_setup()
@func_name_defining
def add_tl_event_reaction(*args, **kwargs):
    return common_add_func(func_name=kwargs.get('this_func_name'), req_data=args[0].data)


@api_view(['POST'])
@docstring_setup()
def edit_timeline_event(request):
    try:
        data = request.data

        category = False
        event_template = False
        event_obj = False

        created_at = datetime.strptime(data['created_at'][:19], '%Y-%m-%d %H:%M:%S') 
        created_at = created_at.replace(tzinfo=timezone.utc)

        cat = data['event_category']
        link = data['link']
        event_tmpl = data['event_template']
        event_txt = data['event']
        event_id = data['event_id']
        emotion = data['emotion']

        category = TimelineEventCategory.objects.filter(category_name=cat).first()
        event_template = TimelineEventTemplate.objects.filter(event_category=category, event=event_tmpl).first()
        event_obj = UsersTimelineEvent.objects.filter(pk=event_id).first()

        if category and event_txt and emotion and event_template and event_obj:
            try:
                event_obj.emotion = emotion
                event_obj.category = category
                event_obj.event_template = event_template
                event_obj.event = event_txt 
                event_obj.created_at = created_at
                event_obj.link = link
                event_obj.save()

                res = {'res': 'good', 'data': {'res_status': 'successfully edited event!'}}
                status=http_status.HTTP_200_OK
            except Exception as e:
                err = f'Error in Editing timeline_event: {e}'
                res = {'res': 'error', 'data': {'error': err}}
                status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': 'incoming data is not valid'}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)


@api_view(['POST'])
@docstring_setup()
def delete_timeline_event(request):
    try:
        data = request.data

        inc_email = data['email']
        inc_name = data['name']
        event_id = data['event_id']

        user = DiaryUser.objects.filter(email=inc_email.lower(), name=inc_name).first()
        if user:
            event = UsersTimelineEvent.objects.filter(pk=event_id).first()
            if event:
                try:
                    event.delete()

                    res = {'res': 'good', 'data': {'res_status': 'successfully deleted event!'}}
                    status=http_status.HTTP_200_OK
                except Exception as e:
                    err = f'Error in deliting timeline_event: {e}'
                    res = {'res': 'error', 'data': {'error': err}}
                    status=http_status.HTTP_400_BAD_REQUEST
            else:
                res = {'res': 'error', 'data': {'error': 'incoming data error: such event is not found'}}
                status=http_status.HTTP_400_BAD_REQUEST
        else:
            res = {'res': 'error', 'data': {'error': 'checked email/name data is not founded'}}
            status=http_status.HTTP_400_BAD_REQUEST
    except Exception as e:
        res = {'res': 'error', 'data': {'error': f'{e}'}}
        status=http_status.HTTP_400_BAD_REQUEST

    return Response(res, status=status)