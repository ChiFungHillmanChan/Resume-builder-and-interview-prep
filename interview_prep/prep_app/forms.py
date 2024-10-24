from django import forms
from .models import Resume, WorkExperience, Education, Skill

class JobInfoForm(forms.Form):
    job_role = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=100)
    job_description = forms.CharField(widget=forms.Textarea)

class UserProfileForm(forms.Form):
    OPPORTUNITY_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('graduate_scheme', 'Graduate Scheme'),
        ('graduate_job', 'Graduate Job'),
        ('postgraduate_study', 'Postgraduate Study'),
        ('placement', 'Placement'),
    ]

    SECTOR_CHOICES = [
       ('accounting_finance', 'Accounting & Finance'),
        ('agriculture_animals_plants', 'Agriculture, Animals & Plants'),
        ('banking_insurance_financial_services', 'Banking, Insurance & Financial Services'),
        ('charity_public_civil_service', 'Charity, Public & Civil Service'),
        ('consulting', 'Consulting'),
        ('creative_arts_design', 'Creative Arts & Design'),
        ('engineering', 'Engineering'),
        ('hospitality_sport_leisure_tourism', 'Hospitality, Sport, Leisure & Tourism'),
        ('hr_recruitment', 'HR & Recruitment'),
        ('investment_banking_fund_management', 'Investment Banking & Fund Management'),
        ('languages_libraries_culture', 'Languages, Libraries & Culture'),
        ('law', 'Law'),
        ('management_business', 'Management & Business'),
        ('marketing_advertising_pr', 'Marketing, Advertising & PR'),
        ('media_journalism_publishing', 'Media, Journalism & Publishing'),
        ('medical_healthcare_dental', 'Medical, Healthcare & Dental'),
        ('procurement_supply_chain', 'Procurement & Supply Chain'),
        ('property_construction_qs', 'Property, Construction & QS'),
        ('retail_business_commercial_services', 'Retail, Business & Commercial Services'),
        ('science_rd_food_industry', 'Science, R&D, Food Industry'),
        ('teaching_education', 'Teaching & Education'),
        ('technology', 'Technology'),

    ]

    opportunity_types = forms.MultipleChoiceField(
        choices=OPPORTUNITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    sectors = forms.MultipleChoiceField(
        choices=SECTOR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    preferred_locations = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter preferred office locations, one per line."
    )
    education = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Enter your educational background."
    )
    diversity = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Optional: Share any diversity information you'd like us to know."
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="List your key skills, separated by commas."
    )
    languages = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="List languages you speak, with proficiency levels."
    )
    cv = forms.FileField(
        label="Upload your CV",
        help_text="Accepted formats: PDF, DOC, DOCX"
    )

class CVAnalysisForm(forms.Form):
    job_role = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=100)
    job_description = forms.CharField(widget=forms.Textarea)
    cv_file = forms.FileField()

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'professional_summary': forms.Textarea(attrs={'rows': 4}),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        exclude = ['resume', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['resume', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ['resume', 'order']
