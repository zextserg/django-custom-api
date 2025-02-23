# Django with custom Admin section and REST framework API

## Description
It's a classic Django app for some "Diary" service, but with useful customisation for different use cases.  
In django Admin section it's for example - managing Many-To-Many relations in different ways, ability to Upload image/audio files through admin UI or through POST request as base64 value, and then ability to show images or listen audios in admin management system.  
It's contains a djangorestframework API with representing of possible GET and POST requests to the service and with ability to test them on the main page.  
Also it contains a django management command wich can be run as bash command.  

## Diary app
In Diary app every **Diary User** have several options how to fill his diary:  
- create an **Entry** - it's like note or post with additional features apart from just text: user can add an image and audio and some tags to the **Entry**
  For **Entry** user can select pre-defined **EntryCategory** and several **EntryTag**.
- create a **Journey** - it's like a story of some trip with text description and linking some countries
  For **Journey** user can select pre-defined **JourneyType** and several **JourneyCountry**.
- pass different Polls (**QuestionsGroups**) - it's like sets of questions with some choices for the answer and calculating total score
  For every pre-defined **Question** in pre-defined **QuestionsGroup** (Poll) user can select answer from pre-defined **Choices** and then it will be saved as **UserAnswer**.  
  It is assumed that user answer to all questions of some Poll on the client side and then all his answers sending to API as POST request.  
  Then it will be saved as **UserCompletedPoll** model and all **UserAswers** model connected to this **UserCompletedPoll**.  
  But also there is ann ability to add just one **UserAswers** via POST request, so then before it you should create **UserCompletedPoll** for this **QuestionsGroup** as like mark that this exact User starts competing this exact Poll, but not finished yet. And then all **UserAnswers** will be carefully attached to one **UserCompletedPoll** object.
- also every **Diary User** have a **UserTimeline** which can be fill with different **Events**
  For adding **TimelineEvent** user should choose category from pre-defined **TimelineEventCategory** and then select one of pre-defined **TimelineEventTemplate** connected to this category.  
  It is assumed that **TimelineEventCategory** and **TimelineEventTemplate** it's a depending DropDownLists on client side.  
  But user can edit **Template** text and add **Event** with some custom data not necessary equal **Template**.
  Also for **Event** user can add any Description and Link as text and also an Emotion - also as text, but it's assumed that on client side it's a pickable choosing from pre-defined list of const smiles.
  - for every **TimelineEvent** user can add **TimelineEventReaction**
    For adding **TimelineEventReaction** user should choose category from pre-defined **TimelineEventReactionCategory** and also add some text data for Reaction, Description and Emotion - also as text, but it's assumed that on client side it's a pickable choosing from pre-defined list of const smiles.
  - there is an API endpoint for Editing **UserTimelineEvent**
    It is assumed that on client side Editing **TimelineEvent** will be also with depending DropDownLists for changing **TimelineEventCategory** and **TimelineEventTemplate**.  
    For that purpose there is an endpoint `get_tl_event_cats_with_templates` which for exact event_id respond with list of **Categories** where first category - it's a current choosen for this event (so it will appear as "choosen" in DroipDownList) and with list of **Templates** where first template - it's a current choosen for this event (so it will appear as "choosen" in DroipDownList)
  - there is an API endpoint for Deleting **UserTimelineEvent**
  - also on **UserTimeline** will appear automatic **Events** like "Registration in App" or "Passed some Poll" with Category "App Achivements" 


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

## REST framework API
From client side this app can receive several GET and POST requests.  
It was made using lib djangorestframework ([link](https://www.django-rest-framework.org/)).  
All possible endpoints is shown as dict with links at main page http://127.0.0.1/  

All endpoints divided for 2 Sections:
- GET API endpoint
- POST API endpoints  

On each link you can open specific Endpoint Page and then will be detailed description what's can be done with this Endpoint, which params can be set and there will be Example link for testing in GET endpoints and Example JSON data for testing POST endpoints.  

Here is view of main page:  
<img width="1055" alt="api_all_list" src="https://github.com/user-attachments/assets/81850890-f49d-490f-9b73-07c0e02d1e92" />

### Section of POST endpoints
On the Page of some POST Endpoint you can find a placeholder at the bottom - here you can insert an Example JSON from description and test the exact request with this data using Button "POST" underneath it:  
<img width="873" alt="django_api_post_example" src="https://github.com/user-attachments/assets/12e8e0d2-a79c-468a-885d-6f7d2fe58b0c" />

Using POST API endpoints Diary User can interact with service and he can create from client side: 
- create Diary user (some sort of Registration in service, but very basic and insecure, just for test)
  for each Diary User will be created also:
  - new User Timeline for that user
  - new User Timeline Event on the Timeline for that new user
    (event: "Registration in app" with category: "App Achievements")   
- create Entry with image/audio using base64 encoded string values
  Then base64 values will be converted to binary and saved in DB as BinaryField.
  Admin can see or listen actual image/audio in Django Admin section.
  In API Example there are base64 examples of real image and audion, but very small ones, for not disturb viewving with very long base64 strings on the page.  
- create Journey with list of Countries
- create User Answers, User Completed Polls  or both at the same endpoint `add_user_answers_with_cp`
- create User Timeline  (basicly it will be auto-created when Diary User is creating)
- create, edit or delete User Timeline Events
- create User Timeline Event Reactions

## Customised Admin Section
From Django Admin UI with SuperUser you can see all data in all models and also add any data to any models.  
There are several usecase features:
- Management of Many-To-Many relation between 2 models are implemented in 2 different views:
  - one is using available/choosen placeholders:
    <img width="1437" alt="django_many_to_many" src="https://github.com/user-attachments/assets/fe397ded-3982-483f-9484-b9505433be0b" />
  - another is using classic approach with one placeholder with contex dropdown, you can see example of it in Adding Entry below with EntryTag field:
- Uploading image/audio using "Browse Files" button in Adding Entry page, then it will be converted to binary and saved in DB as BinaryField:
  (also here you can see other approach of management of Many-To-Many relation in the EntryTag field)
  <img width="685" alt="django_upload_file" src="https://github.com/user-attachments/assets/caee0e01-689f-4797-8328-f403d7e25ece" />
- Ability to show and listen image/audio on the Entry model page - for audio there is a small inline player:
  <img width="1424" alt="django_show_listen_ui" src="https://github.com/user-attachments/assets/8e8faa4f-cb0e-49a8-803d-60bd8b145153" />

## Django Management Command
There is an example of Django Management Command script - it's for inserting first needed values into DB, but also it shows the way how to create scripts which can be run with defauld django command in terminal:  
`python manage.py initial_admin_insert_into_database`



