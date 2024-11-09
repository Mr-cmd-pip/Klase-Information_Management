import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Student, Course, Announcement, Assignment, Submission, Material, Instructor
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from .forms import AnnouncementForm, AssignmentForm, CourseForm, MaterialForm, RegisterForm
from django.contrib.auth.hashers import make_password, check_password
from django import forms
from django.core import validators
import logging

from django import forms


logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

def is_student_authorised(request, code):
    course = Course.objects.get(code=code)
    if request.session.get('student_email') and course in Student.objects.get(email=request.session['student_email']).course.all():
        return True
    else:
        return False

def is_instructor_authorised(request, code):
    if request.session.get('instructor_email') and code in Course.objects.filter(Instructor_id=request.session['instructor_id']).values_list('code', flat=True):
        return True
    else:
        return False

def deleteCourse(request, code):
    if request.session.get('instructor_email'):
        try:
            instructor = Instructor.objects.get(email=request.session['instructor_email'])
            course = Course.objects.get(code=code, Instructor=instructor)
            course.delete()
            messages.success(request, 'Course deleted successfully.')
            return redirect('instructorCourses')
        except Course.DoesNotExist:
            messages.error(request, 'Course does not exist or you do not have permission to delete this course.')
            return redirect('instructorCourses')
    else:
        return redirect('std_login')

def landing(request):
    return render(request, 'landing.html')

# register view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('std_login')  # Redirect to login page after successful registration
    else:
        form = RegisterForm()

    return render(request, 'registration_page.html', {'form': form})

# Custom Login page for both student and instructor
def std_login(request):
    error_messages = []

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            student = Student.objects.filter(email=email).first()
            instructor = Instructor.objects.filter(email=email).first()

            if student and (check_password(password, student.password) or password == student.password):
                request.session['student_email'] = email
                request.session['student_id'] = str(student.student_id)  # Convert UUID to string
                return redirect('myCourses')
            elif instructor and (check_password(password, instructor.password) or password == instructor.password):
                request.session['instructor_email'] = email
                request.session['instructor_id'] = str(instructor.instructor_id)  # Convert UUID to string
                print(f"Instructor Email: {email}")
                return redirect('instructorCourses')
            else:
                error_messages.append('Invalid login credentials.')
        else:
            error_messages.append('Invalid form data.')
    else:
        form = LoginForm()

    if 'student_email' in request.session:
        return redirect('/my/')
    elif 'instructor_email' in request.session:
        return redirect('/instructorCourses/')

    context = {'form': form, 'error_messages': error_messages}
    return render(request, 'login_page.html', context)

# Clears the session on logout
def std_logout(request):
    request.session.flush()
    return redirect('std_login')


# Display all courses (student view)
def myCourses(request):
    try:
        if request.session.get('student_email'):
            student = Student.objects.get(email=request.session['student_email'])
            
            courses = student.course.all()
     
            instructor = student.course.all().values_list('Instructor_id', flat=True)
        

            context = {
                'courses': courses,
                'student': student,
                'instructor': instructor
            }

            return render(request, 'main/myCourses.html', context)
        else:
            return redirect('std_login')
    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'error.html')


# Display all courses (instructor view)
def instructorCourses(request):
    print(f"Session: {request.session['instructor_email']}")
    try:
        if request.session['instructor_email']:
            instructor = Instructor.objects.get(
                email=request.session['instructor_email'])
            print(f"Instructor ID: {instructor.instructor_id}")
            courses = Course.objects.filter(
                Instructor=instructor)
            print(f"Courses: {courses}")
            # Student count of each course to show on the instructor page
            studentCount = Course.objects.all().annotate(student_count=Count('students'))
            print(f"Student Count: {studentCount}")
            studentCountDict = {}

            for course in studentCount:
                studentCountDict[course.code] = course.student_count
            print(f"Student Count Dict: {studentCountDict}")

            context = {
                'courses': courses,
                'instructor': instructor,
                'studentCount': studentCountDict
            }

            return render(request, 'main/instructorCourses.html', context)

        else:
            return redirect('std_login')
    except:

        return redirect('std_login')


# Particular course page (student view)
def course_page(request, code):
    try:
        print(f"Session Data: {request.session.items()}")
     
        course = Course.objects.get(code=code)
        print(f"course: {course}")
        if is_student_authorised(request, code):
            try:
                announcements = Announcement.objects.filter(course_code=course)
                print(f"Announcements: {announcements}")
                assignments = Assignment.objects.filter(course_code=course.code)
                print(f"Assignments: {assignments}")
                materials = Material.objects.filter(course_code=course.code)
                print(f"Materials: {materials}")
            except Exception as e:
                print(f"Error fetching course data: {e}")
                announcements = None
                assignments = None
                materials = None

            context = {
                'course': course,
                'announcements': announcements,
                'assignments': assignments,
                'materials': materials,
                'student': Student.objects.get(email=request.session['student_email'])
            }
            return render(request, 'main/course.html', context)
        else:
            return redirect('std_login')
    except Course.DoesNotExist:
        print("Course does not exist.")
        return redirect('std_login')
    except Exception as e:
        print(f"Unexpected error: {e}")
        return redirect('std_login')
    
# Particular course page (instructor view)
def course_page_instructor(request, code):
    course = Course.objects.get(code=code)
    if request.session.get('instructor_email'):
        try:
            announcements = Announcement.objects.filter(course_code=course)
            assignments = Assignment.objects.filter(course_code=course.code)
            materials = Material.objects.filter(course_code=course.code)
            studentCount = Student.objects.filter(course=course).count()

            context = {
                'course': course,
                'announcements': announcements,
                'assignments': assignments[:3],
                'materials': materials,
                'instructor': Instructor.objects.get(email=request.session['instructor_email']),
                'studentCount': studentCount
            }

            return render(request, 'main/instructor_course.html', context)
        except Exception as e:
            print(f"Error: {e}")
            return redirect('std_login')
    else:
        return redirect('std_login')


def error(request):
    return render(request, 'error.html')


# Display user profile(student & instructor)
def profile(request, email):
    try:
        if 'student_email' in request.session and request.session['student_email'] == email:
            student = Student.objects.get(email=email)
            return render(request, 'main/profile.html', {'student': student})
        elif 'instructor_email' in request.session and request.session['instructor_email'] == email:
            instructor = Instructor.objects.get(email=email)
            return render(request, 'main/instructor_profile.html', {'instructor': instructor})
        else:
            return redirect('std_login')
    except Student.DoesNotExist:
        logger.error(f"Student with email {email} does not exist.")
        return render(request, 'error.html', {'message': 'Student not found.'})
    except Instructor.DoesNotExist:
        logger.error(f"Instructor with email {email} does not exist.")
        return render(request, 'error.html', {'message': 'Instructor not found.'})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return render(request, 'error.html', {'message': 'An unexpected error occurred.'})


def addAnnouncement(request, code):
    if is_instructor_authorised(request, code):
        print('passed')
        if request.method == 'POST':
            form = AnnouncementForm(request.POST)
            form.instance.course_code = Course.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Announcement added successfully.')
                return redirect('/instructor/' + str(code))
        else:
            form = AnnouncementForm()
        return render(request, 'main/announcement.html', {'course': Course.objects.get(code=code), 'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']), 'form': form})
    else:
        return redirect('std_login')


def deleteAnnouncement(request, code, id):
    if is_instructor_authorised(request, code):
        try:
            announcement = Announcement.objects.get(course_code=code, id=id)
            announcement.delete()
            messages.warning(request, 'Announcement deleted successfully.')
            return redirect('/instructor/' + str(code))
        except:
            return redirect('/instructor/' + str(code))
    else:
        return redirect('std_login')


def editAnnouncement(request, code, id):
    if is_instructor_authorised(request, code):
        announcement = Announcement.objects.get(course_code_id=code, id=id)
        form = AnnouncementForm(instance=announcement)
        context = {
            'announcement': announcement,
            'course': Course.objects.get(code=code),
            'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']),
            'form': form
        }
        return render(request, 'main/update-announcement.html', context)
    else:
        return redirect('std_login')


def updateAnnouncement(request, code, id):
    if is_instructor_authorised(request, code):
        try:
            announcement = Announcement.objects.get(course_code_id=code, id=id)
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                messages.info(request, 'Announcement updated successfully.')
                return redirect('/instructor/' + str(code))
        except:
            return redirect('/instructor/' + str(code))

    else:
        return redirect('std_login')


def addAssignment(request, code):
    if is_instructor_authorised(request, code):
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES)
            form.instance.course_code = Course.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(request, 'Assignment added successfully.')
                return redirect('/instructor/' + str(code))
        else:
            form = AssignmentForm()
        return render(request, 'main/assignment.html', {'course': Course.objects.get(code=code), 'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']), 'form': form})
    else:
        return redirect('std_login')


def assignmentPage(request, code, id):
    course = Course.objects.get(code=code)
    if is_student_authorised(request, code):
        assignment = Assignment.objects.get(course_code=course.code, id=id)
        try:

            submission = Submission.objects.get(assignment=assignment, student=Student.objects.get(
                student_id=request.session['student_id']))

            context = {
                'assignment': assignment,
                'course': course,
                'submission': submission,
                'time': datetime.datetime.now(),
                'student': Student.objects.get(student_id=request.session['student_id']),
                'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
            }

            return render(request, 'main/assignment-portal.html', context)

        except:
            submission = None

        context = {
            'assignment': assignment,
            'course': course,
            'submission': submission,
            'time': datetime.datetime.now(),
            'student': Student.objects.get(student_id=request.session['student_id']),
            'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
        }

        return render(request, 'main/assignment-portal.html', context)
    else:

        return redirect('std_login')


def allAssignments(request, code):
    if is_instructor_authorised(request, code):
        course = Course.objects.get(code=code)
        assignments = Assignment.objects.filter(course_code=course)
        studentCount = Student.objects.filter(course=course).count()

        context = {
            'assignments': assignments,
            'course': course,
            'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']),
            'studentCount': studentCount

        }
        return render(request, 'main/all-assignments.html', context)
    else:
        return redirect('std_login')


def allAssignmentsSTD(request, code):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        assignments = Assignment.objects.filter(course_code=course)
        context = {
            'assignments': assignments,
            'course': course,
            'student': Student.objects.get(student_id=request.session['student_id']),

        }
        return render(request, 'main/all-assignments-std.html', context)
    else:
        return redirect('std_login')


def addSubmission(request, code, id):
    try:
        course = Course.objects.get(code=code)
        if is_student_authorised(request, code):
            # check if assignment is open
            assignment = Assignment.objects.get(course_code=course.code, id=id)
            if assignment.deadline < datetime.datetime.now():

                return redirect('/assignment/' + str(code) + '/' + str(id))

            if request.method == 'POST' and request.FILES['file']:
                assignment = Assignment.objects.get(
                    course_code=course.code, id=id)
                submission = Submission(assignment=assignment, student=Student.objects.get(
                    student_id=request.session['student_id']), file=request.FILES['file'],)
                submission.status = 'Submitted'
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                assignment = Assignment.objects.get(
                    course_code=course.code, id=id)
                submission = Submission.objects.get(assignment=assignment, student=Student.objects.get(
                    student_id=request.session['student_id']))
                context = {
                    'assignment': assignment,
                    'course': course,
                    'submission': submission,
                    'time': datetime.datetime.now(),
                    'student': Student.objects.get(student_id=request.session['student_id']),
                    'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
                }

                return render(request, 'main/assignment-portal.html', context)
        else:
            return redirect('std_login')
    except:
        return HttpResponseRedirect(request.path_info)


def viewSubmission(request, code, id):
    try:
        course = Course.objects.get(code=code)
    except Course.DoesNotExist:
        messages.error(request, 'Course does not exist.')
        return redirect('instructorCourses')

    if is_instructor_authorised(request, code):
        try:
            assignment = Assignment.objects.get(course_code_id=code, id=id)
            submissions = Submission.objects.filter(assignment_id=assignment.id)

            context = {
                'course': course,
                'submissions': submissions,
                'assignment': assignment,
                'totalStudents': Student.objects.filter(course=course).count(),
                'instructor': Instructor.objects.get(email=request.session['instructor_email']),
                'courses': Course.objects.filter(Instructor__email=request.session['instructor_email'])
            }

            return render(request, 'main/assignment-view.html', context)

        except Assignment.DoesNotExist:
            messages.error(request, 'Assignment does not exist.')
            return redirect('/instructor/' + str(code))
        except Instructor.DoesNotExist:
            messages.error(request, 'Instructor does not exist.')
            return redirect('std_login')
        except Exception as e:
            messages.error(request, f'Unexpected error: {e}')
            return redirect('/instructor/' + str(code))
    else:
        return redirect('std_login')


def gradeSubmission(request, code, id, sub_id):
    try:
        course = Course.objects.get(code=code)
    except Course.DoesNotExist:
        messages.error(request, 'Course does not exist.')
        return redirect('instructorCourses')

    if is_instructor_authorised(request, code):
        try:
            assignment = Assignment.objects.get(course_code_id=code, id=id)
            submission = Submission.objects.get(assignment_id=assignment.id, id=sub_id)

            if request.method == 'POST':
                submission.marks = request.POST['marks']
                if request.POST['marks'] == '0':
                    submission.marks = 0
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                submissions = Submission.objects.filter(assignment_id=assignment.id)

                context = {
                    'course': course,
                    'submissions': submissions,
                    'assignment': assignment,
                    'totalStudents': Student.objects.filter(course=course).count(),
                    'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']),
                    'courses': Course.objects.filter(Instructor__instructor_id=request.session['instructor_id'])
                }

                return render(request, 'main/assignment-view.html', context)

        except Assignment.DoesNotExist:
            messages.error(request, 'Assignment does not exist.')
            return redirect('/instructor/' + str(code))
        except Submission.DoesNotExist:
            messages.error(request, 'Submission does not exist.')
            return redirect('/instructor/' + str(code))
        except Instructor.DoesNotExist:
            messages.error(request, 'Instructor does not exist.')
            return redirect('std_login')
        except Exception as e:
            messages.error(request, f'Unexpected error: {e}')
            return redirect('/error/')
    else:
        return redirect('std_login')

def addCourse(request):
    if request.session.get('instructor_email'):
        instructor = Instructor.objects.get(email=request.session['instructor_email'])
        
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.Instructor = instructor
                course.save()
                messages.success(request, 'Course created successfully.')
                return redirect('instructorCourses')
        else:
            form = CourseForm()
        
        context = {
            'form': form,
            'instructor': instructor
        }
        
        return render(request, 'main/addCourse.html', context)
    else:
        return redirect('std_login')

def addCourseMaterial(request, code):
    if is_instructor_authorised(request, code):
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            form.instance.course_code = Course.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(request, 'New course material added')
                return redirect('/instructor/' + str(code))
            else:
                return render(request, 'main/course-material.html', {'course': Course.objects.get(code=code), 'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']), 'form': form})
        else:
            form = MaterialForm()
            return render(request, 'main/course-material.html', {'course': Course.objects.get(code=code), 'instructor': Instructor.objects.get(instructor_id=request.session['instructor_id']), 'form': form})
    else:
        return redirect('std_login')


def deleteCourseMaterial(request, code, id):
    if is_instructor_authorised(request, code):
        course = Course.objects.get(code=code)
        course_material = Material.objects.get(course_code=course, id=id)
        course_material.delete()
        messages.warning(request, 'Course material deleted')
        return redirect('/instructor/' + str(code))
    else:
        return redirect('std_login')
    
def edit_course(request, code):
    if request.session.get('instructor_email'):
        try:
            course = Course.objects.get(code=code, Instructor__email=request.session['instructor_email'])
        except Course.DoesNotExist:
            messages.error(request, 'Course does not exist or you do not have permission to edit this course.')
            return redirect('instructorCourses')

        if request.method == 'POST':
            form = CourseForm(request.POST, instance=course)
            if form.is_valid():
                form.save()
                messages.success(request, 'Course updated successfully.')
                return redirect('instructorCourses')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = CourseForm(instance=course)

        context = {
            'form': form,
            'instructor': Instructor.objects.get(email=request.session['instructor_email'])
        }
        return render(request, 'main/editCourse.html', context)
    else:
        return redirect('std_login')

def withdraw_course(request, code):
    if request.session.get('student_email'):
        try:
            student = Student.objects.get(email=request.session['student_email'])
            course = Course.objects.get(code=code)
            student.course.remove(course)
            student.save()
            messages.success(request, 'You have successfully withdrawn from the course.')
            return redirect('myCourses')
        except Course.DoesNotExist:
            messages.error(request, 'Course does not exist.')
            return redirect('myCourses')
        except Student.DoesNotExist:
            messages.error(request, 'Student does not exist.')
            return redirect('std_login')
    else:
        return redirect('std_login')

def courses(request):
    if request.session.get('student_email') or request.session.get('instructor_email'):

        courses = Course.objects.all()
        student = None
        instructor = None

        if request.session.get('student_email'):
            student = Student.objects.get(email=request.session['student_email'])
        if request.session.get('instructor_email'):
            instructor = Instructor.objects.get(email=request.session['instructor_email'])

        enrolled = student.course.all() if student else None
        accessed = Course.objects.filter(Instructor=instructor) if instructor else None
        print(accessed)

        context = {
            'instructor': instructor,
            'courses': courses,
            'student': student,
            'enrolled': enrolled,
            'accessed': accessed
        }

        return render(request, 'main/all-courses.html', context)

    else:
        return redirect('std_login')



def access(request, code):
    if request.session.get('student_email'):
        course = Course.objects.get(code=code)
        print(course)
        student = Student.objects.get(email=request.session['student_email'])
        print(student.email)
        if request.method == 'POST':
            if (request.POST['key']) == str(course.studentKey):
                student.course.add(course)
                student.save()
                return redirect('/my/')
            else:
                messages.error(request, 'Invalid key')
                return HttpResponseRedirect(request.path_info)
        else:
            return render(request, 'main/access.html', {'course': course, 'student': student})

    else:
        return redirect('std_login')


def search(request):
    if request.session.get('student_id') or request.session.get('instructor_id'):
        if request.method == 'GET' and request.GET['q']:
            q = request.GET['q']
            courses = Course.objects.filter(
                Q(code__icontains=q) | 
                Q(title__icontains=q) | 
                Q(Instructor__name__icontains=q) | # Correct field name
                Q(description__icontains=q) 
            )

            student = None
            instructor = None
            if request.session.get('student_id'):
                student = Student.objects.get(student_id=request.session['student_id'])
            if request.session.get('instructor_id'):
                instructor = Instructor.objects.get(instructor_id=request.session['instructor_id'])

            enrolled = student.course.all() if student else None
            accessed = Course.objects.filter(Instructor=instructor) if instructor else None

            context = {
                'courses': courses,
                'instructor': instructor,
                'student': student,
                'enrolled': enrolled,
                'accessed': accessed,
                'q': q
            }
            return render(request, 'main/search.html', context)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('std_login')

def changePasswordPrompt(request):
    if request.session.get('student_email'):
        student = Student.objects.get(email=request.session['student_email'])
        return render(request, 'main/changePassword.html', {'student': student})
    elif request.session.get('instructor_id'):
        instructor = Instructor.objects.get(instructor_id=request.session['instructor_id'])
        return render(request, 'main/changePasswordInstructor.html', {'instructor': instructor})
    else:
        return redirect('std_login')


def changePhotoPrompt(request):
    if request.session.get('student_email'):
        student = Student.objects.get(email=request.session['student_email'])
        return render(request, 'main/changePhoto.html', {'student': student})
    elif request.session.get('instructor_email'):
        instructor = Instructor.objects.get(email=request.session['instructor_email'])
        return render(request, 'main/changePhotoInstructor.html', {'instructor': instructor})
    else:
        return redirect('std_login')


def changePassword(request):
    if request.session.get('student_id'):
        student = Student.objects.get(
            student_id=request.session['student_id'])
        if request.method == 'POST':
            if student.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                student.password = request.POST['newPassword']
                student.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/profile/' + str(student.student_id))
            else:
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePassword/')
        else:
            return render(request, 'main/changePassword.html', {'student': student})
    else:
        return redirect('std_login')


def changePasswordInstructor(request):
    if request.session.get('instructor_id'):
        instructor = Instructor.objects.get(
            instructor_id=request.session['instructor_id'])
        if request.method == 'POST':
            if instructor.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                instructor.password = request.POST['newPassword']
                instructor.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/instructorProfile/' + str(instructor.instructor_id))
            else:
                print('error')
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePasswordInstructor/')
        else:
            print(instructor)
            return render(request, 'main/changePasswordInstructor.html', {'instructor': instructor})
    else:
        return redirect('std_login')


def changePhoto(request):
    if request.session.get('student_id'):
        student = Student.objects.get(
            student_id=request.session['student_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                student.photo = request.FILES['photo']
                student.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/profile/' + str(student.student_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhoto/')
        else:
            return render(request, 'main/changePhoto.html', {'student': student})
    else:
        return redirect('std_login')


def changePhotoInstructor(request):
    if request.session.get('instructor_id'):
        instructor = Instructor.objects.get(
            instructor_id=request.session['instructor_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                instructor.photo = request.FILES['photo']
                instructor.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/instructorProfile/' + str(instructor.instructor_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhotoInstructor/')
        else:
            return render(request, 'main/changePhotoInstructor.html', {'instructor': instructor})
    else:
        return redirect('std_login')


def guestStudent(request):
    request.session.flush()
    try:
        student = Student.objects.get(name='Guest Student')
        request.session['student_id'] = str(student.student_id)
        return redirect('myCourses')
    except:
        return redirect('std_login')


def guestInstructor(request):
    request.session.flush()
    try:
        instructor = Instructor.objects.get(name='Guest Instructor')
        request.session['instructor_id'] = str(instructor.instructor_id)
        return redirect('instructorCourses')
    except:
        return redirect('std_login')
