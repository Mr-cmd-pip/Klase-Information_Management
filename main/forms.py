from django import forms
from froala_editor.widgets import FroalaEditor
from .models import Announcement, Assignment, Course, Material, Student

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'description', 'title', 'studentKey', 'InstructorKey']
        widgets = {
            'code': forms.NumberInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'maxlength': '50'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'studentKey': forms.NumberInput(attrs={'class': 'form-control'}),
            'InstructorKey': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Course.objects.filter(title=title).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Course with this Title already exists.")
        return title

    def clean_studentKey(self):
        studentKey = self.cleaned_data.get('studentKey')
        if Course.objects.filter(studentKey=studentKey).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Course with this StudentKey already exists.")
        return studentKey

    def clean_InstructorKey(self):
        InstructorKey = self.cleaned_data.get('InstructorKey')
        if Course.objects.filter(InstructorKey=InstructorKey).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Course with this InstructorKey already exists.")
        return InstructorKey

class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['description'].label = ''

    class Meta:
        model = Announcement
        fields = ['description']
        widgets = {
            'description': FroalaEditor(),
        }


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.label = ''
        self.fields['file'].required = False

    class Meta:
        model = Assignment
        fields = ('title', 'description', 'deadline', 'marks', 'file')
        widgets = {
            'description': FroalaEditor(),
            'title': forms.TextInput(attrs={'class': 'form-control mt-1', 'id': 'title', 'name': 'title', 'placeholder': 'Title'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control mt-1', 'id': 'deadline', 'name': 'deadline', 'type': 'datetime-local'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control mt-1', 'id': 'marks', 'name': 'marks', 'placeholder': 'Marks'}),
            'file': forms.FileInput(attrs={'class': 'form-control mt-1', 'id': 'file', 'name': 'file', 'aria-describedby': 'file', 'aria-label': 'Upload'}),
        }


class MaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.label = ""
        self.fields['file'].required = False

    class Meta:
        model = Material
        fields = ('description', 'file')
        widgets = {
            'description': FroalaEditor(),
            'file': forms.FileInput(attrs={'class': 'form-control', 'id': 'file', 'name': 'file', 'aria-describedby': 'file', 'aria-label': 'Upload'}),
        }

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data