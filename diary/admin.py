from django.contrib import admin
from diary import models
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from django.urls import reverse
from django.core.files.uploadedfile import UploadedFile
from django.utils.safestring import mark_safe
import base64


def list_related_items(items, render_as_list=False):
    html = '['
    if items.count() > 0:
        admin_viewname = 'admin:{app_label}_{model_name}_change'.format(
            app_label=items[0]._meta.app_label,
            model_name=items[0]._meta.model_name,
        )

        if render_as_list:
            html += '<ul>'
            for obj in items.all():
                html += '<li><a href="{url}" style="white-space: nowrap; color: blue; text-decoration: underline">{name}</a></li>'.format(
                    url=reverse(admin_viewname, args=(obj.id, )),
                    name=str(obj)[:10]
                )
            html += '</ul>'
        else:
            links = []
            for obj in items.all():
                links.append('<a href="{url}" style="white-space: nowrap; color: blue; text-decoration: underline">{name}</a>'.format(
                    url=reverse(admin_viewname, args=(obj.id, )),
                    name=str(obj)[:10]
                ))
            html += ' | '.join(links)
    html +=']'
    return mark_safe(html)


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['question']


class QuestionAdminForm(forms.ModelForm):
    choices_of_questions = forms.ModelMultipleChoiceField(
        queryset=models.Choice.objects.all(), 
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('choices_of_questions'),
            is_stacked=False
        )
    )

    class Meta:
        model = models.Question
        exclude = []

    def __init__(self, *args, **kwargs):
        super(QuestionAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['choices_of_questions'].initial = self.instance.choices_of_questions.all()

    def save(self, commit=True):
        question = super(QuestionAdminForm, self).save(commit=commit)

        if commit:
            question.choices_of_questions = self.cleaned_data['choices_of_questions']
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                question.choices_of_questions.set(self.cleaned_data['choices_of_questions'])
            self.save_m2m = new_save_m2m

        return question


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['question_text']
    form = QuestionAdminForm
    list_display = [
        'questions_group',
        'question_text',
        'list_choices',
    ]
    def list_choices(self, obj):
        return list_related_items(obj.choices_of_questions.all())
    list_choices.short_description = _('Choices')


@admin.register(models.JourneyCountry)
class JourneyCountryAdmin(admin.ModelAdmin):
    search_fields = ['name']


class JourneyAdminForm(forms.ModelForm):
    class Meta:
        model = models.Journey
        fields = '__all__'


@admin.register(models.Journey)
class JourneyAdmin(admin.ModelAdmin):
    form = JourneyAdminForm
    autocomplete_fields = ['country']

    list_display = [
        'user',
        'title',
        'type',
        'dates',
        'description',
        'link',
        'list_countries',
    ]
    def list_countries(self, obj):
        return list_related_items(obj.country.all())
    list_countries.short_description = 'Countries'


class EntryAdminForm(forms.ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput, required=False)
    audio = forms.FileField(widget=forms.ClearableFileInput, required=False)

    class Meta:
        model = models.Entry
        fields = '__all__'

    def save(self, commit=True):
        try:
            if isinstance(self.cleaned_data.get('image'), UploadedFile) and self.cleaned_data.get('image').name:
                self.instance.image = self.cleaned_data['image'].read()
                self.instance.image_name = self.cleaned_data.get('image').name
                
            if isinstance(self.cleaned_data.get('audio'), UploadedFile) and self.cleaned_data.get('audio').name:
                self.instance.audio = self.cleaned_data['audio'].read()
                self.instance.audio_name = self.cleaned_data.get('audio').name
        except Exception as e:
            print(f'err inn saving uploaded file to binary field: {e}')

        return super(EntryAdminForm, self).save(commit=commit)


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    form = EntryAdminForm
    autocomplete_fields = ['tag']

    def image_display(self, obj):
        if obj and obj.image:
            return mark_safe(f'<img src="data:image/jpeg;base64,{base64.b64encode(obj.image).decode()}" width="150" />')
        else:
            return "No image"
    image_display.short_description = 'Image Display'

    def image_bytes(self, obj):
        if obj and obj.image:
            return base64.b64encode(obj.image).decode()[:20]
        else:
            return 'No image'
    image_bytes.short_description = 'Image Bytes'

    def audio_play(self, obj):
        if obj and obj.audio:
            return mark_safe(f'<audio controls name="media"><source src="data:audio/mpeg;base64,{base64.b64encode(obj.audio).decode()}" type="audio/mpeg"></audio>')
        else:
            return "No audio"
    audio_play.short_description = 'Audio Play'

    def audio_bytes(self, obj):
        if obj and obj.audio:
            return base64.b64encode(obj.audio).decode()[:20]
        else:
            return 'No audio'
    audio_bytes.short_description = 'Audio Bytes'
    
    def list_tags(self, obj):
        return list_related_items(obj.tag.all())
    list_tags.short_description = 'Tags'

    readonly_fields = ('image_name', 'image_display', 'image_bytes', 'audio_name',  'audio_play', 'audio_bytes')
    list_display = ('title', 'date_time', 'description', 'text', 'category', 'list_tags', 'image_name', 'image_display', 'image_bytes', 'audio_name',  'audio_play', 'audio_bytes')


@admin.register(models.EntryTag)
class EntryTagAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.EntryCategory)
admin.site.register(models.QuestionsGroup)
admin.site.register(models.DiaryUser)
admin.site.register(models.UsersAnswer)
admin.site.register(models.UsersCompletedPoll)
admin.site.register(models.UsersTimeline)
admin.site.register(models.TimelineEventCategory)
admin.site.register(models.UsersTimelineEvent)
admin.site.register(models.EventReactionCategory)
admin.site.register(models.UsersTimelineEventReaction)
admin.site.register(models.TimelineEventTemplate)
admin.site.register(models.JourneyType)