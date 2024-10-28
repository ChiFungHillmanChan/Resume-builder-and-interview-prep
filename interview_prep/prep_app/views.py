import re
import ast 
import google.generativeai as genai
import io
import PyPDF2
import subprocess
import tempfile
import json 
import os

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import (LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView)
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import JobInfoForm, UserProfileForm, CVAnalysisForm, ResumeForm, WorkExperienceForm, EducationForm, SkillForm, CustomAuthenticationForm, CustomUserCreationForm, CodeSubmissionForm
from .models import Resume, WorkExperience, Education, Skill, Topic, Question, UserSubmission, UserCode


genai.configure(api_key=settings.GEMINI_API_KEY)

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'prep_app/login_logout_folder/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        username = form.cleaned_data.get('username')
        
        # Call parent's form_valid to authenticate user
        response = super().form_valid(form)
        
        if remember_me:
            # Set session expiry to 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)
            
            # Set cookie for username
            response.set_cookie(
                'remembered_username',
                username,
                max_age=30 * 24 * 60 * 60,  # 30 days
                httponly=True,  # Cookie not accessible via JavaScript
                samesite='Strict'  # CSRF protection
            )
        else:
            # Delete the cookie if "remember me" is not checked
            response.delete_cookie('remembered_username')
            self.request.session.set_expiry(0)
            
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Invalid username or password. Please try again.',
            extra_tags='error'
        )
        return super().form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill username if cookie exists
        remembered_username = self.request.COOKIES.get('remembered_username')
        if remembered_username:
            initial['username'] = remembered_username
        return initial

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # Log the user in after registration
            login(request, user)
            messages.success(request, f'Account created successfully for {username}')
            return redirect('login')
        else:
            # If form is not valid, errors will be shown in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'prep_app/login_logout_folder/register.html', {'form': form})


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
        result['cv_skills'] = [skill.strip(" '").replace("'", "") for skill in cv_skills_match.group(1).split(',')]
        
    # Parse missing_skills
    missing_skills_match = re.search(r"'missing_skills':\s*\[(.*?)\]", clean_response, re.DOTALL)
    if missing_skills_match:
        result['missing_skills'] = [skill.strip(" '").replace("'", "") for skill in missing_skills_match.group(1).split(',')]
    
    # Parse match_score
    match_score_match = re.search(r"'match_score':\s*(\d+)", clean_response)
    if match_score_match:
        result['match_score'] = int(match_score_match.group(1))
    
    for i in result['cv_skills']:
        i = i.replace("'", "")
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
    
    return render(request, 'prep_app/resume_builder.html', context)

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


def customer_support(request):
    return render(request, 'prep_app/customer_support.html')


def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'prep_app/topic_list.html', {
        'topics': topics
    })

def question_list(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    questions = topic.questions.all()
    return render(request, 'prep_app/question_list.html', {
        'topic': topic,
        'questions': questions
    })

@login_required
def coding_assessment(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.question = question
            submission.save()
            
            # Here you would typically run the code against test cases
            # For now, we'll just return a success response
            return JsonResponse({
                'status': 'success',
                'message': 'Code submitted successfully'
            })
    else:
        form = CodeSubmissionForm(initial={'code': question.initial_code})

    return render(request, 'prep_app/coding_assessment.html', {
        'question': question,
        'form': form,
        'initial_code': question.initial_code,
        'submissions': UserSubmission.objects.filter(
            user=request.user,
            question=question
        ).order_by('-created_at')[:5]
    })

@login_required
@csrf_protect
def run_code(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        language = data.get('language', 'python')
        
        # Get the question and test cases
        question = get_object_or_404(Question, id=question_id)
        test_cases = question.test_cases
        title = question.title
        
        # Generate a filename based on the question title and language
        function_name = title.replace(" ", "_").lower()
        sanitized_title = ''.join(c for c in function_name if c.isalnum() or c == '_')
        
        # Define file extensions and run commands for each language
        language_configs = {
            'python': {
                'extension': '.py',
                'command': ['python'],
                'function_template': 'result = {}({})',
            },
            'java': {
                'extension': '.java',
                'command': ['java'],
                'function_template': 'result = solution.{}({})',
            },
            'javascript': {
                'extension': '.js',
                'command': ['node'],
                'function_template': 'result = {}({})',
            },
            'cpp': {
                'extension': '.cpp',
                'command': ['g++', '-o'],
                'function_template': 'result = {}({})',
            }
        }
        
        if language not in language_configs:
            return JsonResponse({'status': 'error', 'message': 'Unsupported language'}, status=400)
        
        temp_dir = '/Users/hillmanchan/Desktop/interview_prep_proj/interview_prep/static/temp_files'
        config = language_configs[language]
        file_name = os.path.join(temp_dir, f"{sanitized_title}{config['extension']}")
        
        # Extract function name from the initial code template based on language
        initial_code_dict = json.loads(question.initial_code) if isinstance(question.initial_code, str) else question.initial_code
        function_pattern = {
            'python': r'def\s+(\w+)\s*\(',
            'java': r'public\s+\w+\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(',
            'cpp': r'\w+\s+(\w+)\s*\('
        }
        
        match = re.search(function_pattern[language], initial_code_dict[language])
        if match:
            actual_function_name = match.group(1)
        else:
            return JsonResponse({'status': 'error', 'message': 'Could not extract function name'}, status=400)
        
        # Write code to language-specific file
        with open(file_name, 'w') as f:
            if language == 'java':
                f.write('public class Solution {\n')
                f.write(code)
                f.write('\n    public static void main(String[] args) {\n')
                f.write('        Solution solution = new Solution();\n')

            elif language == 'javascript':
                f.write(code)
                f.write('\n\nconst results = [];\n')

            elif language == 'cpp':
                f.write('#include <iostream>\n#include <vector>\n#include <string>\n#include <json/json.h>\n')
                f.write(code)
                f.write('\n\nint main() {\n')
                
            else:  # python
                f.write(code)
                f.write('\n\n# Test runner\n')
                f.write('import json\n')
                f.write('results = []\n')
            
            # Add test cases according to language
            for i, test_case in enumerate(test_cases):
                test_input = test_case.get('input', {})
                expected_output = test_case.get("expected", "No expected output")
                
                if isinstance(test_input, dict) and len(test_input) > 1:
                    params_str = ', '.join([f"{k}={repr(v)}" for k, v in test_input.items()])
                else:
                    params_str = json.dumps(test_input)
                
                if language == 'python':
                    f.write(f'\ntry:\n')
                    f.write(f'    result = {actual_function_name}({params_str})\n')
                    f.write(f'    results.append({{"index": {i}, "actual_output": result, "expected": {json.dumps(expected_output)}, "passed": result == {json.dumps(expected_output)}}})\n')
                    f.write('except Exception as e:\n')
                    f.write(f'    results.append({{"index": {i}, "actual_output": str(e), "expected": {json.dumps(expected_output)}, "passed": False}})\n')
                
                # Add language-specific test runners here for other languages...
                # Modify the language handling part in run_code function:
                elif language == 'java':
                    write_java_test_file(file_name, code, test_cases, actual_function_name)
            # Close the main function/class for compiled languages
            if language == 'java':
                f.write('    }\n}')
            elif language == 'cpp':
                f.write('    return 0;\n}')
            
            if language == 'python':
                f.write('\nprint(json.dumps(results))\n')
        
        # Execute the code based on language
        try:
            if language == 'python':
                process = subprocess.run(
                    ['python', file_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if process.returncode == 0:
                    test_results = json.loads(process.stdout)
                    all_passed = all(result['passed'] for result in test_results)
                    return JsonResponse({
                        'status': 'success',
                        'test_results': test_results,
                        'all_passed': all_passed
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Execution error: {process.stderr}'
                    })
            else:
                # Add execution logic for other languages here
                return JsonResponse({
                    'status': 'error',
                    'message': f'Language {language} execution not implemented yet'
                })
                
        except subprocess.TimeoutExpired:
            return JsonResponse({
                'status': 'error',
                'message': 'Code execution timed out'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing request: {str(e)}'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing request: {str(e)}'
        }, status=400)

    
@login_required
@require_http_methods(["POST"])
def save_code(request, question_id):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        language = data.get('language')
        
        # Update or create the UserCode instance
        user_code, created = UserCode.objects.update_or_create(
            user=request.user,
            question_id=question_id,
            language=language,
            defaults={'code': code}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Code saved successfully',
            'last_modified': user_code.last_modified.isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_saved_code(request, question_id):
    try:
        language = request.GET.get('language', 'python')  # Default to python
        user_code = UserCode.objects.filter(
            user=request.user,
            question_id=question_id,
            language=language
        ).first()
        
        print (user_code.code, user_code.language)
        if user_code:
            return JsonResponse({
                'status': 'success',
                'code': user_code.code,
                'language': user_code.language,
                'last_modified': user_code.last_modified.isoformat()
            })
        else:
            return JsonResponse({
                'status': 'not_found',
                'code': None
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    

def write_java_test_file(file_name, code, test_cases, actual_function_name):
    """Write a properly formatted Java test file."""
    with open(file_name, 'w') as f:
        # Add imports
        f.write('import java.util.*;\n')
        f.write('import org.json.*;\n\n')
        
        # Start Solution class
        f.write('public class Solution {\n')
        
        # Write the submitted solution code (without the class declaration)
        if 'public class Solution' in code:
            # Extract just the method from the submitted code
            method_start = code.find('{') + 1
            method_end = code.rfind('}')
            f.write(code[method_start:method_end])
        else:
            f.write(code)
        
        # Add main method for testing
        f.write('\n    public static void main(String[] args) {\n')
        f.write('        Solution solution = new Solution();\n')
        f.write('        List<Map<String, Object>> results = new ArrayList<>();\n\n')
        
        # Add test cases
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get('input', [])
            expected_output = test_case.get('expected')
            
            f.write(f'        // Test case {i + 1}\n')
            f.write('        try {\n')
            
            # Handle input array
            array_str = ', '.join(str(x) for x in test_input)
            f.write(f'            int[] nums = new int[]{{{array_str}}};\n')
            
            # Call method and store result
            f.write(f'            int result = solution.{actual_function_name}(nums);\n')
            
            # Create result map
            f.write('            Map<String, Object> testResult = new HashMap<>();\n')
            f.write(f'            testResult.put("index", {i});\n')
            f.write('            testResult.put("actual_output", result);\n')
            f.write(f'            testResult.put("expected", {expected_output});\n')
            f.write(f'            testResult.put("passed", result == {expected_output});\n')
            f.write('            results.add(testResult);\n')
            
            # Add catch block
            f.write('        } catch (Exception e) {\n')
            f.write('            Map<String, Object> testResult = new HashMap<>();\n')
            f.write(f'            testResult.put("index", {i});\n')
            f.write('            testResult.put("actual_output", e.toString());\n')
            f.write(f'            testResult.put("expected", {expected_output});\n')
            f.write('            testResult.put("passed", false);\n')
            f.write('            results.add(testResult);\n')
            f.write('        }\n\n')
        
        # Add JSON output
        f.write('        // Convert results to JSON and print\n')
        f.write('        System.out.println(new JSONArray(results).toString());\n')
        
        # Close main method and class
        f.write('    }\n')
        f.write('}\n')

