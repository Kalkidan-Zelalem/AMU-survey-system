# surveys/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction

from .models import Survey, Question, Choice, Response, Answer, Profile
from .forms import (
    SurveyCreateForm, QuestionCreateForm, # Our new forms for the create page
    QuestionForm, ChoiceFormSet             # Your original forms for the update page
)

# Your helper function is perfect.
def is_creator_or_staff(user):
    """A helper function to identify a survey creator by their 'is_staff' status."""
    return user.is_staff

# ==============================================================================
# === THE NEW SINGLE-PAGE SURVEY CREATION VIEW (REPLACES SurveyCreateView) ===
# ==============================================================================

@login_required
@user_passes_test(is_creator_or_staff)
def survey_create_view(request):
    """
    A view to create a survey and its questions (with choices) on a single page.
    """
    QuestionFormSet = inlineformset_factory(
        Survey,
        Question,
        form=QuestionCreateForm,
        extra=1,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )

    if request.method == 'POST':
        survey_form = SurveyCreateForm(request.POST)
        formset = QuestionFormSet(request.POST, prefix='questions')

        if survey_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                survey = survey_form.save(commit=False)
                survey.creator = request.user
                survey.save()

                for i, form in enumerate(formset):
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        question = form.save(commit=False)
                        question.survey = survey
                        question.order = i
                        question.save()

                        choices_text = form.cleaned_data.get('choices_text')
                        if choices_text and question.question_type in [Question.QuestionType.CHOICE, Question.QuestionType.MULTIPLE_CHOICE]:
                            choices_list = [choice.strip() for choice in choices_text.splitlines() if choice.strip()]
                            for choice_text in choices_list:
                                Choice.objects.create(question=question, text=choice_text)
                
                for form in formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()

            messages.success(request, f"Survey '{survey.title}' created successfully!")
            # THIS LINE IS ALREADY CORRECT and does not need to be changed.
            return redirect('surveys:survey-detail', pk=survey.pk)
    else:
        survey_form = SurveyCreateForm()
        formset = QuestionFormSet(prefix='questions')

    context = {
        'survey_form': survey_form,
        'formset': formset,
        'page_title': 'Create New Survey'
    }
    return render(request, 'surveys/survey_create_page.html', context)


# ==============================================================================
# === YOUR EXISTING VIEWS (WITH ALL REDIRECTS CORRECTED) ===
# ==============================================================================

class SurveyListView(LoginRequiredMixin, ListView):
    # This view has no redirects, so it is already correct.
    model = Survey
    template_name = 'surveys/survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        if is_creator_or_staff(user):
            return Survey.objects.filter(creator=user).order_by('-created_at')
        else:
            queryset = Survey.objects.filter(is_active=True)
            queryset = queryset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now)
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            )
            if hasattr(user, 'profile'):
                user_role = user.profile.user_type
                queryset = queryset.filter(Q(target_audience='ALL') | Q(target_audience=user_role))
            else:
                queryset = queryset.filter(target_audience='ALL')

            taken_survey_ids = Response.objects.filter(respondent=user).values_list('survey__id', flat=True)
            queryset = queryset.exclude(pk__in=taken_survey_ids)
            return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_creator'] = is_creator_or_staff(self.request.user)
        return context


class SurveyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Survey
    fields = ['title', 'description', 'target_audience', 'is_active', 'start_date', 'end_date','is_public']
    template_name = 'surveys/survey_form.html'
    def test_func(self): return self.request.user == self.get_object().creator
    def get_success_url(self):
        messages.success(self.request, "Survey settings updated successfully.")
        
        # === THIS IS THE FIX ===
        # Add the 'surveys:' namespace to the redirect.
        return reverse('surveys:survey-detail', kwargs={'pk': self.object.pk})

class SurveyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Survey
    template_name = 'surveys/survey_confirm_delete.html'
    
    # === THIS IS THE FIX ===
    # Add the 'surveys:' namespace to the redirect.
    success_url = reverse_lazy('surveys:survey-list')
    
    def test_func(self): return self.request.user == self.get_object().creator
    def form_valid(self, form):
        messages.success(self.request, f"The survey '{self.object.title}' has been successfully deleted.")
        return super().form_valid(form)

class SurveyDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # This view has no redirects, so it is already correct.
    model = Survey
    template_name = 'surveys/survey_detail.html'
    def test_func(self):
        return self.request.user == self.get_object().creator or self.request.user.is_superuser
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_creator'] = self.request.user == self.get_object().creator or self.request.user.is_superuser
        return context

class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'surveys/question_form.html'
    def test_func(self): return self.request.user == self.get_object().survey.creator
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST, instance=self.object)
        else:
            context['choice_formset'] = ChoiceFormSet(instance=self.object)
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choice_formset']
        if choice_formset.is_valid():
            self.object = form.save()
            choice_formset.instance = self.object
            choice_formset.save()
            messages.success(self.request, "Question updated successfully.")
            
            # === THIS IS THE FIX ===
            # Add the 'surveys:' namespace to the redirect.
            return redirect('surveys:survey-detail', pk=self.object.survey.pk)
        else: return self.render_to_response(self.get_context_data(form=form))

class SurveyTakeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # Your get_object and test_func methods are preserved and correct.
    model = Survey
    template_name = 'surveys/survey_take_form.html'
    def get_object(self, queryset=None):
        if 'public_id' in self.kwargs:
            return get_object_or_404(
                Survey, 
                public_id=self.kwargs['public_id'], 
                is_public=True,
                is_active=True
            )
        return super().get_object(queryset)
    def test_func(self):
        survey = self.get_object()
        user = self.request.user
        now = timezone.now()
        if user == survey.creator: return False
        if Response.objects.filter(survey=survey, respondent=user).exists(): return False
        if 'public_id' in self.kwargs:
            return True
        if not survey.is_active: return False
        if survey.start_date and now < survey.start_date: return False
        if survey.end_date and now > survey.end_date: return False
        if hasattr(user, 'profile'):
            if survey.target_audience != 'ALL' and survey.target_audience != user.profile.user_type: return False
        elif survey.target_audience != 'ALL': return False
        return True
    
    def post(self, request, *args, **kwargs):
        # Your post logic for saving answers is preserved and correct.
        survey = self.get_object()
        response = Response.objects.create(survey=survey, respondent=request.user)
        for question in survey.questions.all():
            answer = Answer(response=response, question=question)
            q_type = question.question_type
            if q_type in [Question.QuestionType.TEXT, Question.QuestionType.TEXTAREA, Question.QuestionType.RATING]:
                answer.body = request.POST.get(f'question_{question.id}')
                answer.save()
            elif q_type == Question.QuestionType.CHOICE:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    answer.save()
                    answer.choices.add(Choice.objects.get(id=choice_id))
            elif q_type == Question.QuestionType.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                if choice_ids:
                    answer.save()
                    answer.choices.add(*choice_ids)
        
        # This line is already correct and does not need to be changed.
        return redirect('surveys:survey-thank-you')

class SurveyResultsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # This view has no redirects, so it is already correct.
    model = Survey
    template_name = 'surveys/survey_results.html'
    def test_func(self): return self.request.user == self.get_object().creator or self.request.user.is_superuser

class SurveyThankYouView(LoginRequiredMixin, TemplateView):
    # This view has no redirects, so it is already correct.
    template_name = 'surveys/survey_thank_you.html'