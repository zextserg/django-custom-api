# Django with custom Admin section and REST framework API

## Description
It's a classic Django app for some "Diary" service, but with useful customisation for different use cases.  
In django Admin section it's for example - managing Many-To-Many relations in different ways, ability to Upload image/audio files through admin UI or through POST request as base64 value, and then ability to show images or listen audios in admin management system.  
It's contains a djangorestframework API with representing of possible GET and POST requests to the service and with ability to test them on the main page.  
Also it contains a django management command wich can be run as bash command.  

## Diary app
In Diary app every Diary User have several options how to fill his diary:  
- create an Entry - it's like note or post with additional features apart from just text: user can add an image and audio and some tags to the Entry
  For Entry user can select pre-defined EntryCategory and several EntryTag.
- create a Journey - it's like a story of some trip with text description and linking some countries
  For Journey user can select pre-defined JourneyType and several JourneyCountry.
- pass different Polls (QuestionsGroups) - it's like sets of questions with some choices for the answer and calculating total score
  For every pre-defined Question in pre-defined QuestionsGroup (Poll) user can select answer from pre-defined Choices and then it will be saved as UserAnswer.  
  It is assumed that user answer to all questions of some Poll on the client side and then all his answers sending to API as POST request.  
  Then it will be saved as UserCompletedPoll model and all UserAswers model connected to this UserCompletedPoll.  
  But also there is ann ability to add just one UserAswers via POST request, so then before it you should create UserCompletedPoll for this QuestionsGroup as like mark that this exact User starts competing this exact Poll, but not finished yet. And then all UserAnswers will be carefully attached to one UserCompletedPoll object.
- also every Diary User have a UserTimeline which can be fill with different Events
  For adding TimelineEvent user should choose category from pre-defined TimelineEventCategory and then select one of pre-defined TimelineEventTemplate connected to this category.  
  It is assumed that TimelineEventCategory and TimelineEventTemplate it's a depending DropDownLists on client side.  
  But user can edit Template text and add Event with some custom data not necessary equal Template.
  Also for Event user can add any Description and Link as text and also an Emotion - also as text, but it's assumed that on client side it's a pickable choosing from pre-defined list of const smiles.
  - for every TimelineEvent user can add TimelineEventReaction
    For adding TimelineEventReaction user should choose category from pre-defined TimelineEventReactionCategory and also add some text data for Reaction, Description and Emotion - also as text, but it's assumed that on client side it's a pickable choosing from pre-defined list of const smiles.
  - there is an API endpoint for Editing UserTimelineEvent
    It is assumed that on client side Editing TimelineEvent will be also with depending DropDownLists for changing TimelineEventCategory and TimelineEventTemplate.  
    For that purpose there is an endpoint `/api/get_tl_event_cats_with_templates` which for exact event_id respond with list of Categories where first category - it's a current choosen for this event (so it will appear as "choosen" in DroipDownList) and with list of Templates where first template - it's a current choosen for this event (so it will appear as "choosen" in DroipDownList)
  - there is an API endpoint for Deleting UserTimelineEvent
  - also on UserTimeline will appear automatic Events like "Registration in App" or "Passed some Poll" with Category "App Achivements" 


## Run and test
For succesfull running and testing all Examples in API you should make connection to some Database and create tables in it according to Migrations file and also fill these tables with first values nedded for proper work of examples requests.  

###  connection to DB
connection to database should be configured in main_settings dir in settings.py file ([here](main_configs/settings.py#L62)). 
  
By default it is connected to SQLite3 database which will be named "diary_app_db.sqlite3".  
Here you can edit it and connect to some other, like Postgres.

### making migrations
The project already contains a migrations file "001_initial.py" in "/diary/migrations" dir ([here](diary/migrations/0001_initial.py)).  

So basicly all you need - is run in terminal command:  
`python manage.py migrate`  
and then will be created sqlite3 DB (diary_app_db.sqlite3) and then will be created all tables in DB for this app (according to migrations file) and then will be created internal Django tables in DB (for Auth and Admin sections).  

But if for some reason you want re-create migrations file or don't want to use existing - just run command:  
`python manage.py makemigrations`  
and then will be created sqlite3 DB (diary_app_db.sqlite3) and then will be created migrations for tables in DB for this app (according to models.py file) - you will see the appered file in "/diary/migrations" dir ([here](diary/migrations/))

### Runing app for the first time
After creating all tables in DB you need to create a SuperUser for Django Admin section. For that just run in terminal command:  
`python manage.py createsuperuser`  
and follow prompt in terminal, then you will be able to access Admin section on the link http://127.0.0.1/admin  

After creating SuperUser you can finally Run the App with command in terminal:  
`python manage.py runserver`  

### Inserting initial data into DB
For using and testing all REST API endpoints - before it Admin should insert several first values to some tables in DB.  
Here is a list what should be done and with such exact values - then All examples in REST API endpoints descriptions will work.  
But if don't want to test these API examples - you don't need to make this initial insert into DB.  
You can insert your own values and start using service with them.  
One more time - this script insert first values only for the reason that REST API examples will not throw errors if you try them as described in each enndpoint.  

For inserting all needed values you have 2 options:  
- you can use already existing script "initial_admin_insert_into_database.py" ([here](diary/management/commands/initial_admin_insert_into_database.py)).  
  It was created as DjangoManagementCommand, so you can run it as command in terminal:  
  `python manage.py initial_admin_insert_into_database`  
  and then it will insert all needed values into DB and print the results of inserting (or errors) in terminal.  
- you can add all needed values manualy in Admin section (http://127.0.0.1/admin).
  So here is a list which values for which models you need to add as Admin:
  - insert into **Entry Categories** 1 value:  
    {"name": "Notes"}
  - insert into **Entry Tags** 2 values:  
    {"name": "note"}, {"name": "long-read"}
  - insert into **Journey Types** 1 value:  
    {"name": "just for weekend"}
  - insert into **Journey Countries** 2 values:  
    {"name": "United Kingdome", "lang": "english", "flag": "🇬🇧"}   
    {"name": "France", "lang": "french", "flag": "🇫🇷"}  
  - insert into **Questions groups** 1 value:  
    {"group_name": "Group1", "max_score": 25, "result_types": {"good": [0,13], "bad": [14,25]}}  
    with QuestionGroup also will be inserted first values for **Timeline event categories** with values:
    {"id": 1, "category_name": "App Achievements"}  
  - insert into **Questions** 2 values:  
    {"question_text": "Is this question awesome?", "order": 1, "questions_group": 1} (without any choices)  
    {"question_text": "Another question is better?", "order": 2, "questions_group": 1} (without any choices)  
  - insert into **Choices** 2 values:  
    {"choice_text": "Yes, it**s awesome!", "order": 1, "question": [1, 2]}  
    {"choice_text": "No, it**s even better!", "order": 2, "question": [1, 2]}  
  - insert into **Timeline event categories** 1 value:  
    {"category_name": "Good Events"}  
    this value will not be first, but second, because first value was inserted with **QuestionGroup** (above). So this value will be with id = 2  
  - insert into **Timeline event templates** 1 value:  
    {"event": "Some Good Event", "event_category": 2}  
    in these values we set event_category = 2 because it's first meaningful **EventCategory** and **EventCategory** with id = 1 was technical "App Achievements"  
  - insert into **Timeline event reaction category** 1 value:  
    {"category_name": "Happy reactions"}  


Admin create:
- Entry Categories - {"Name": "Notes"}
- Entry Tags - [{"Name": "Notes"}, {"Name": "long-read"}]
- Journey Types - {"Name": "just for weekend"}
- Journey Countries - [
    {"Name": "United Kingdome", "Lang": "english", "Flag": "🇬🇧"},
    {"Name": "France", "Lang": "french", "Flag": "🇫🇷"},
]
- Questions groups - {"Group name": "Group1", "Max score": 25, "Result_types": {"good": [0,13], "bad": [14,25]}}
- Choices - [
    {"Choice text": "Yes, it's awesome!", "Order": 1} (without any question),
    {"Choice text": "No, it's even better!", "Order": 2} (without any question),
]
- Questions - [
    {"Question text": "Is this question awesome?", "Order": 1} 
    (with Question_group = "Group1" and choice = "Yes, it's awesome!"), 
    {"Question text": "Another question is better?", "Order": 2} 
    (with Question_group = "Group1" and choice = "No, it's even better!")
]
- Timeline event categorys - {"Category name": "Good Events"}
- Timeline event templates - {"Event": "Some Good Event"} (in cat = "Good Events")
- Timeline event reaction category - {"Category name": "Happy reactions"}

API creates via POST:
- Diary user
- Entry
- Journeys
- Users completed polls
- Users answers
- Users timeline event reactions
- Users timeline events
- Users timelines
