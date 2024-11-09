import datetime
from django.shortcuts import redirect, render
from discussion.models import InstructorDiscussion, StudentDiscussion
from main.models import Student, Instructor, Course
from main.views import is_instructor_authorised, is_student_authorised
from itertools import chain



def context_list(course):
    try:
        studentDis = StudentDiscussion.objects.filter(course=course)
        instructorDis = InstructorDiscussion.objects.filter(course=course)
        discussions = list(chain(studentDis, instructorDis))
        discussions.sort(key=lambda x: x.sent_at, reverse=True)

        for dis in discussions:
            if dis.__class__.__name__ == 'StudentDiscussion':
                dis.author = Student.objects.get(student_id=dis.sent_by_id)
            else:
                dis.author = Instructor.objects.get(instructor_id=dis.sent_by_id)
    except:
        discussions = []

    return discussions


def discussion(request, code):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        student = Student.objects.get(email=request.session['student_email'])
        discussions = context_list(course)
        context = {
            'course': course,
            'student': student,
            'discussions': discussions,
        }
        return render(request, 'discussion/discussion.html', context)

    elif is_instructor_authorised(request, code):
        course = Course.objects.get(code=code)
        instructor = Instructor.objects.get(email=request.session['instructor_email'])
        discussions = context_list(course)
        context = {
            'course': course,
            'instructor': instructor,
            'discussions': discussions,
        }
        return render(request, 'discussion/discussion.html', context)
    else:
        return redirect('std_login')


def send(request, code, email):
    if is_student_authorised(request, code):
        if request.method == 'POST':
            content = request.POST['content']
            course = Course.objects.get(code=code)
            student = Student.objects.get(email=email)
            try:
                StudentDiscussion.objects.create(
                    content=content,
                    course=course,
                    sent_by=student,
                    sent_at=datetime.datetime.now()
                )
                return redirect('discussion', code=code)
            except:
                return redirect('discussion', code=code)

    else:
        return render(request, 'error.html')


def send_fac(request, code, email):
    if is_instructor_authorised(request, code):
        if request.method == 'POST':
            content = request.POST['content']
            course = Course.objects.get(code=code)
            try:
                instructor = Instructor.objects.get(email=email)
                InstructorDiscussion.objects.create(
                    content=content,
                    course=course,
                    sent_by=instructor,
                    sent_at=datetime.datetime.now()
                )
                return redirect('discussion', code=code)
            except:
                return redirect('discussion', code=code)
    else:
        return render(request, 'error.html')