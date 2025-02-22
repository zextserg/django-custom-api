from rest_framework import serializers
from diary.models import *


class DiaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryUser
        fields = '__all__'


class UsersCompletedPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersCompletedPoll
        fields = '__all__'


class QuestionsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionsGroup
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class UsersAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersAnswer
        fields = '__all__'


class UsersTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersTimeline
        fields = '__all__'


class TimelineEventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEventCategory
        fields = '__all__'


class TimelineEventTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEventTemplate
        fields = '__all__'


class UsersTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersTimelineEvent
        fields = '__all__'


class EventReactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReactionCategory
        fields = '__all__'


class UsersTimelineEventReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersTimelineEventReaction
        fields = '__all__'


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = '__all__'


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = '__all__'