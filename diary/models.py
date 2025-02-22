from django.db import models

TECHNICAL_TL_CATEGORY = 'App Achievements'
TECH_TL_QG_PASSED_EVENT_TEMPLATE = 'Passed {questions_group_name} poll'
TECH_TL_REG_NU_EVENT_TEMPLATE = 'Registration in App'

class QuestionsGroup(models.Model):
    class Meta:
        db_table = 'questions_groups'
    
    group_name = models.CharField(max_length=100, unique=True)
    group_title = models.CharField(max_length=100, null=True, blank=True)
    group_description = models.CharField(max_length=500, null=True, blank=True)
    group_time_to_pass = models.CharField(max_length=100, null=True, blank=True)
    group_frequency = models.CharField(max_length=100, null=True, blank=True)
    max_score = models.IntegerField(null=True)
    result_types = models.JSONField(
        """result_types:
JSON with types of questions group results: 
keys - names of types; 
values - lists with exact 2 integers for range of scores.
For example:
{"good": [0,13], "bad": [14,25]}""", null=True) 

    def __str__(self):
        return self.group_name
    
    def save(self, **kwargs):
        super().save(**kwargs)  # Call the "real" save() method.
        tech_tl_event_cat = TimelineEventCategory.objects.filter(category_name=TECHNICAL_TL_CATEGORY).first()
        if not tech_tl_event_cat:
            tech_tl_event_cat = TimelineEventCategory(category_name=TECHNICAL_TL_CATEGORY)
            tech_tl_event_cat.save()

        tl_event = TECH_TL_QG_PASSED_EVENT_TEMPLATE.format(questions_group_name=self.group_name)
        tl_event_template = TimelineEventTemplate(event_category=tech_tl_event_cat, event=tl_event)
        tl_event_template.save()


class Question(models.Model):
    class Meta:
        db_table = 'questions'
    
    questions_group = models.ForeignKey(QuestionsGroup, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    class Meta:
        db_table = 'choices'
    
    question = models.ManyToManyField(Question, blank=True, null=True, related_name='choices_of_questions')
    choice_text = models.CharField(max_length=500)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.choice_text


class DiaryUser(models.Model):
    class Meta:
        db_table = 'diary_users'
    
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.email = self.email.lower()
        super().save(**kwargs)  # Call the "real" save() method.


class UsersCompletedPoll(models.Model):
    class Meta:
        db_table = 'users_completed_polls'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    questions_group = models.ForeignKey(QuestionsGroup, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}; qst_grp: {str(self.questions_group)[:20]}; dt: {self.completed_at}"
    

class UsersAnswer(models.Model):
    class Meta:
        db_table = 'users_answers'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Choice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_completed_poll = models.ForeignKey(UsersCompletedPoll, on_delete=models.CASCADE)

    def __str__(self):
        return f"user: {self.user}; qst: {str(self.question)[:20]}; ans: {str(self.answer)[:20]}; dt: {self.created_at}"


class UsersTimeline(models.Model):
    class Meta:
        db_table = 'users_timelines'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    start_dt = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"user: {self.user}; start_dt: {self.start_dt}"


class TimelineEventCategory(models.Model):
    class Meta:
        db_table = 'timeline_event_categories'
    
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class TimelineEventTemplate(models.Model):
    class Meta:
        db_table = 'timeline_event_templates'
    
    event_category = models.ForeignKey(TimelineEventCategory, on_delete=models.CASCADE)
    event = models.CharField(max_length=200)

    def __str__(self):
        return f'event_cat: {self.event_category}, event: {self.event}'


class UsersTimelineEvent(models.Model):
    class Meta:
        db_table = 'users_timeline_events'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    timeline = models.ForeignKey(UsersTimeline, on_delete=models.CASCADE)
    category = models.ForeignKey(TimelineEventCategory, on_delete=models.CASCADE)
    event_template = models.ForeignKey(TimelineEventTemplate, on_delete=models.CASCADE)
    event = models.CharField(max_length=500, null=True, blank=True)
    link = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    emotion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"user: {self.user}; event: {str(self.event)[:20]}; created_at: {self.created_at}"


class EventReactionCategory(models.Model):
    class Meta:
        db_table = 'event_reaction_categories'
    
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
    

class UsersTimelineEventReaction(models.Model):
    class Meta:
        db_table = 'users_timeline_event_reactions'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    event = models.ForeignKey(UsersTimelineEvent, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    category = models.ForeignKey(EventReactionCategory, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    emotion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"user: {self.user}; event: {str(self.event)[:20]}; reaction: {str(self.reaction)[:20]}; created_at: {self.created_at}"


class JourneyType(models.Model):
    class Meta:
        db_table = 'journey_types'
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class JourneyCountry(models.Model):
    class Meta:
        db_table = 'journey_countries'
    
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=100)
    flag = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.flag})'


class Journey(models.Model):
    class Meta:
        db_table = 'journeys'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    type = models.ForeignKey(JourneyType, on_delete=models.CASCADE)
    dates = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    link = models.CharField(max_length=500, null=True, blank=True)
    country = models.ManyToManyField(JourneyCountry, blank=True, null=True, related_name='journeys_of_country')

    def __str__(self):
        return self.title


class EntryTag(models.Model):
    class Meta:
        db_table = 'entry_tags'
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EntryCategory(models.Model):
    class Meta:
        db_table = 'entry_categories'
    
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Entry(models.Model):
    class Meta:
        db_table = 'entries'
    
    user = models.ForeignKey(DiaryUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date_time = models.DateTimeField(null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    image = models.BinaryField(null=True, blank=True, editable=True)
    image_name = models.CharField(max_length=100, null=True, blank=True)
    audio = models.BinaryField(null=True, blank=True, editable=True)
    audio_name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(EntryCategory, on_delete=models.CASCADE)
    tag = models.ManyToManyField(EntryTag, blank=True, null=True, related_name='entries_of_tag')

    def __str__(self):
        return self.title
