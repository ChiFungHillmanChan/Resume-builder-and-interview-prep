import re
import ast 
import google.generativeai as genai
import io
import PyPDF2

from django.contrib.auth.views import (LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView)
from django import forms
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import JobInfoForm, UserProfileForm, CVAnalysisForm, ResumeForm, WorkExperienceForm, EducationForm, SkillForm
from .models import Resume, WorkExperience, Education, Skill


genai.configure(api_key=settings.GEMINI_API_KEY)

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}
    ))

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'prep_app/login_logout_folder/login.html'
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        else:
            # Session expires in 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'prep_app/login_logout_folder/password_reset_form.html'
    email_template_name = 'prep_app/login_logout_folder/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'prep_app/login_logout_folder/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'prep_app/login_logout_folder/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'prep_app/login_logout_folder/password_reset_complete.html'


def register(request):
    if request.method == 'POST':

        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'prep_app/login_logout_folder/register.html', {'form':form})


def analyze_job_description(job_role, company_name, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Analyze the following job description for {job_role} at {company_name}:

    {job_description}

    Provide the following information:
    1. Simplified job description (2-3 sentences)
    2. Skills required (return as a list)
    3. Key benefits (return as a list)
    4. Future interview process steps (list of 4-5 likely steps)

    Format the output as a Python dictionary with keys: 'simplified_description', 'skills', 'benefits', and 'interview_steps'.
    """
    
    response = model.generate_content(prompt)
    clean_response = response.text.replace("```python", "").replace("```", "").strip()

    print (clean_response)
    analysis = ast.literal_eval(clean_response.strip())

    # analysis['skills'] = [skill.strip() for skill in analysis['skills'].split(",")]
    # analysis['benefits'] = [benefit.strip() for benefit in analysis['benefits'].split(".") if benefit]

    return analysis

@login_required(login_url='/login/')
def ai_job_info(request):
    if request.method == 'POST':
        form = JobInfoForm(request.POST)
        if form.is_valid():
            job_role = form.cleaned_data['job_role']
            company_name = form.cleaned_data['company_name']
            job_description = form.cleaned_data['job_description']
        
            analysis = analyze_job_description(job_role, company_name, job_description)

            return render(request, 'prep_app/job_info_results.html', {'analysis': analysis, 'job_role': job_role, 'company_name': company_name})
        
    else:
        form = JobInfoForm()
    return render(request, 'prep_app/job_info.html', {'form': form})

def home(request):
    return render(request, 'prep_app/home.html')

def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the form data
            # You can save it to the database or pass it to the next step
            # For now, we'll just redirect to the job description page
            return redirect('job_description')
    else:
        form = UserProfileForm()
    
    return render(request, 'user_profile.html', {'form': form})


def parse_ai_response(response_text):
    # Remove any markdown code block syntax
    clean_response = response_text.replace("```python", "").replace("```", "").strip()
    
    # Initialize the result dictionary
    result = {
        'keywords': [],
        'job_skills': [],
        'cv_skills': [],
        'missing_skills': [],
        'match_score': 0
    }
    
    # Parse keywords
    keywords_match = re.search(r"'keywords':\s*\[(.*?)\]", clean_response, re.DOTALL)
    if keywords_match:
        keywords_str = keywords_match.group(1)
        keywords = re.findall(r"\('([^']+)',\s*(\d+)\)", keywords_str)
        result['keywords'] = [{'word': word, 'count': int(count)} for word, count in keywords]
    
    # Parse job_skills
    job_skills_match = re.search(r"'job_skills':\s*\[(.*?)\]", clean_response, re.DOTALL)
    if job_skills_match:
        result['job_skills'] = [skill.strip(" '") for skill in job_skills_match.group(1).split(',')]
    
    # Parse cv_skills
    cv_skills_match = re.search(r"'cv_skills':\s*\[(.*?)\]", clean_response, re.DOTALL)
    if cv_skills_match:
        result['cv_skills'] = [skill.strip(" '") for skill in cv_skills_match.group(1).split(',')]
    
    # Parse missing_skills
    missing_skills_match = re.search(r"'missing_skills':\s*\[(.*?)\]", clean_response, re.DOTALL)
    if missing_skills_match:
        result['missing_skills'] = [skill.strip(" '") for skill in missing_skills_match.group(1).split(',')]
    
    # Parse match_score
    match_score_match = re.search(r"'match_score':\s*(\d+)", clean_response)
    if match_score_match:
        result['match_score'] = int(match_score_match.group(1))
    
    return result

def analyze_cv(job_role, company_name, job_description, cv_content):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Analyze the following CV content against the job description for {job_role} at {company_name}:

    Job Description:
    {job_description}

    CV Content:
    {cv_content}

    Provide the following information:
    1. Keywords from the job description with their occurrence count
    2. Skills mentioned in the job description
    3. Skills found in the CV
    4. Skills missing in the CV but required for the job
    5. Overall match score (percentage)

    Format the output as a Python dictionary with keys: 'keywords', 'job_skills', 'cv_skills', 'missing_skills', and 'match_score'.
    For 'keywords', provide a list of tuples (word, count).
    For other skills lists, provide a list of strings.
    For 'match_score', provide an integer percentage.
    """
    
    response = model.generate_content(prompt)

    # check input token and output token
    # model.input_token_limit / model.output_token_limit

    # count tokens
    # model.count_token(prompt)

    # check response usage
    # response.usage_metadata
    
    analysis = parse_ai_response(response.text)
    return analysis

@login_required(login_url='/login/')
def cv_analysis(request):
    if request.method == 'POST':
        form = CVAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            job_role = form.cleaned_data['job_role']
            company_name = form.cleaned_data['company_name']
            job_description = form.cleaned_data['job_description']
            cv_file = form.cleaned_data['cv_file']

            
            cv_content = ""
            if cv_file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(cv_file.read()))
                for page in pdf_reader.pages:
                    cv_content += page.extract_text()
            else:  
                cv_content = cv_file.read().decode('utf-8')

            analysis = analyze_cv(job_role, company_name, job_description, cv_content)

            return render(request, 'prep_app/cv_analysis_results.html', {
                'analysis': analysis,
                'job_role': job_role,
                'company_name': company_name
            })
        
    else:
        form = CVAnalysisForm()
    return render(request, 'prep_app/cv_analysis.html', {'form': form})

@login_required(login_url='/login/')
def resume_builder(request):
    resume, created = Resume.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal':
            form = ResumeForm(request.POST, instance=resume)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
        
        elif form_type == 'experience':
            experience_id = request.POST.get('experience_id')
            if experience_id:
                experience = WorkExperience.objects.get(id=experience_id)
                form = WorkExperienceForm(request.POST, instance=experience)
            else:
                form = WorkExperienceForm(request.POST)
            
            if form.is_valid():
                experience = form.save(commit=False)
                experience.resume = resume
                experience.save()
                return JsonResponse({'status': 'success'})
    
    context = {
        'resume_form': ResumeForm(instance=resume),
        'experience_form': WorkExperienceForm(),
        'education_form': EducationForm(),
        'skill_form': SkillForm(),
        'resume': resume,
    }
    
    return render(request, 'prep_app/build_resume/resume_builder.html', context)

@login_required(login_url='/login/')
@require_http_methods(["POST"])
def delete_experience(request, experience_id):
    experience = get_object_or_404(WorkExperience, id=experience_id, resume__user=request.user)
    experience.delete()
    return JsonResponse({'status': 'success'})

@login_required(login_url='/login/')
@require_http_methods(["POST"])
def delete_education(request, education_id):
    education = get_object_or_404(Education, id=education_id, resume__user=request.user)
    education.delete()
    return JsonResponse({'status': 'success'})

@login_required(login_url='/login/')
@require_http_methods(["POST"])
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, resume__user=request.user)
    skill.delete()
    return JsonResponse({'status': 'success'})