# Getting started with Django

Adding new Test:
1. Add new Question group (Django Admin)
2. Add questions and choices of test (set order!) (Django Admin)
3. Add timeline event template to App Achivements category with "Passed <group_name> test" name (Django Admin)
4. Add new group to ConstSurveyVariables - set "group_name" & "group_id" as in Django (Xcode)
5. Add new button (Xcode):
5.1. Add button with tite on screen (Xcode Storyboard)
5.2. Set class in properties - VarButton (Xcode Storyboard)
5.3. Connect button to viewController in code - SelfExplorerViewController (Xcode Storyboard + Code)
5.4. Set action to new button in SelfExplorerViewController (Xcode Code)
5.5. Set button.value in func viewDidLoad() in SelfExplorerViewController (Xcode Code)

python manage.py makemigrations - then will be created sqlite3 DB (diary_app_db.sqlite3) and then will be created migrations for tables in DB for this app (according to models.py file)

python manage.py migrate - then will be created tables in DB for this app (according to migrations files) and then will be created internal Django tables in DB (for Auth and Admin sections)

python manage.py createsuperuser - creating user for Admin section (on the link 127.0.0.1/admin)
python manage.py runserver - start using

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