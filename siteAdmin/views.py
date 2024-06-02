import hashlib

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
import requests
import json

from AdminSkyLang.settings import STATIC_URL, MEDIA_URL, MEDIA_ROOT
from .forms import LoginForm, RegisterForm, UserForm, CourseForm, CommentForm, ExerciseForm, LectureForm

from PIL import Image
import io, base64

BASE_API_URL = 'http://127.0.0.1:8080/'


def index(request):
    user_id = request.session.get('user_id')
    token = request.session.get('token')

    if user_id:
        user_url = BASE_API_URL + f'users/{user_id}/'
        response = requests.get(user_url)

        if response.status_code == 200:
            user = response.json()
            return render(request, 'index.html', {'user': user, 'token': token})
        else:
            del request.session['user_id']
            del request.session['token']
            return redirect('login')

    return render(request, 'index.html', {'user': None, 'token': token})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            login_url = BASE_API_URL + 'users/login/'
            login_data = json.dumps({
                "login": form.cleaned_data["login"],
                "password": form.cleaned_data["password"]
            })

            response = requests.post(login_url, data=login_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                user_data = response.json()
                request.session['user_id'] = user_data['id']
                return redirect('index')
            else:
                form.add_error(None, 'Неверный логин или пароль')
                return render(request, 'auth/login.html', {'form': form})

    form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            register_url = BASE_API_URL + 'users/signup/'
            register_data = json.dumps({
                'login': form.cleaned_data['login'],
                'password': form.cleaned_data['password'],
                'email': form.cleaned_data['email'],
                'role': form.cleaned_data['role']
            })
            response = requests.post(register_url, data=register_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('login')
            else:
                form.add_error(None, 'Пользователь с таким именем уже существует')
                return render(request, 'auth/register.html', {'form': form})

    form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']

    return redirect('index')


def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)

        if form.is_valid():
            create_course_url = BASE_API_URL + 'courses/'

            icon = form.cleaned_data['icon']

            if icon:
                image = Image.open(icon)
                image_io = io.BytesIO()
                image.save(image_io, 'PNG')
                image_b64 = base64.b64encode(image_io.getvalue()).decode('utf-8')
                create_course_data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'language': form.cleaned_data['language'],
                    'author': int(form.cleaned_data['author_id']),
                    'icon': str(image_b64)
                }
            else:
                create_course_data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'language': form.cleaned_data['language'],
                    'author': int(form.cleaned_data['author_id']),
                    'icon': ''
                }

            print(create_course_data)

            response = requests.post(create_course_url, data=json.dumps(create_course_data), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('courses')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно создать курс')
                return render(request, 'course/create_course.html', {'form': form})

    form = CourseForm()
    return render(request, 'course/create_course.html', {'form': form})


def update_course(request, course_id):
    form = CourseForm()

    course_url = BASE_API_URL + 'courses/' + str(course_id) + '/'
    response = requests.get(course_url)

    if response.status_code == 200:
        course = response.json()
        form.fields['name'].initial = course['name']
        form.fields['description'].initial = course['description']
        form.fields['language'].initial = course['language']
        form.fields['rating'].initial = course['grates']
        form.fields['author_id'].initial = course['author_id']
    else:
        print(response.json())

    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            update_course_url = BASE_API_URL + 'courses/' + str(course_id) + '/'

            icon = form.cleaned_data['icon']

            if icon:
                image = Image.open(icon)
                image_io = io.BytesIO()
                image.save(image_io, 'PNG')
                image_b64 = base64.b64encode(image_io.getvalue()).decode('utf-8')
                update_course_data = {
                    'id': course_id,
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'language': form.cleaned_data['language'],
                    'grate': float(form.cleaned_data['rating']),
                    'author': int(form.cleaned_data['author_id']),
                    'icon': image_b64
                }
            else:
                update_course_data = {
                    'id': course_id,
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'language': form.cleaned_data['language'],
                    'grate': float(form.cleaned_data['rating']),
                    'author': int(form.cleaned_data['author_id']),
                }

            response = requests.put(update_course_url, data=json.dumps(update_course_data), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('courses')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно обновить курс')
                return render(request, 'course/update_course.html', {'form': form})

    return render(request, 'course/update_course.html', {'form': form})


def delete_course(request, course_id):
    course_url = BASE_API_URL + 'courses/' + str(course_id) + '/'
    response = requests.delete(course_url)

    if response.status_code == 200:
        return redirect('courses')
    else:
        print(response.json())
        return None


def course(request, course_id):
    course_url = BASE_API_URL + 'courses/' + str(course_id) + '/'
    response = requests.get(course_url)

    if response.status_code == 200:
        course = response.json()

        try:
            img = Image.open(io.BytesIO(base64.b64decode(course["icon"])))
            img.save('media/' + course["name"] + '.png')

            course["icon"] = MEDIA_URL + course["name"] + '.png'
            print(course["icon"])

        except:
            course = {
                'id': course['id'],
                'name': course['name'],
                'description': course['description'],
                'language': course['language'],
                'rating': course['rating'],
                'author': course['author'],
                'icon': MEDIA_URL + 'card_1.png'
            }

        return render(request, 'course/course.html', {'course': course})
    else:
        print(response.json())
        return None


def courses(request):
    courses_url = BASE_API_URL + 'courses/'
    response = requests.get(courses_url)

    if response.status_code == 200:
        courses_list = response.json()
        paginator = Paginator(courses_list, 10)  # Show 10 courses per page.

        page = request.GET.get('page')
        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            courses = paginator.page(1)
        except EmptyPage:
            courses = paginator.page(paginator.num_pages)

        return render(request, 'course/courses.html', {'courses': courses})
    else:
        print(response.json())
        return None


def create_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            create_comment_url = BASE_API_URL + 'comments/'
            create_comment_data = json.dumps({
                'course_id': form.cleaned_data['course_id'],
                'author_id': form.cleaned_data['author_id'],
                'content': form.cleaned_data['content']
            })
            response = requests.post(create_comment_url, data=create_comment_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('comments')
            else:
                form.add_error(None, 'Невозможно создать комментарий')
                return render(request, 'comment/create_comment.html', {'form': form})

    form = CommentForm()
    return render(request, 'comment/create_comment.html', {'form': form})


def update_comment(request, comment_id):
    form = CommentForm()

    comment_url = BASE_API_URL + 'comments/' + str(comment_id) + '/'
    response = requests.get(comment_url)

    if response.status_code == 200:
        comment = response.json()
        form.fields['course_id'].initial = comment['course_id']
        form.fields['author_id'].initial = comment['author_id']
        form.fields['content'].initial = comment['content']
    else:
        print(response.json())

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            update_comment_url = BASE_API_URL + 'comments/' + str(comment_id) + '/'
            update_comment_data = {
                'course_id': form.cleaned_data['course_id'],
                'author_id': form.cleaned_data['author_id'],
                'content': form.cleaned_data['content']
            }
            response = requests.put(update_comment_url, data=update_comment_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('comments')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно обновить комментарий')
                return render(request, 'comment/update_comment.html', {'form': form})

    return render(request, 'comment/update_comment.html', {'form': form})


def delete_comment(request, comment_id):
    comment_url = BASE_API_URL + 'comments/' + str(comment_id) + '/'
    response = requests.delete(comment_url)

    if response.status_code == 200:
        return redirect('comments')
    else:
        print(response.json())
        return None


def comment(request, comment_id):
    comment_url = BASE_API_URL + 'comments/' + str(comment_id) + '/'
    response = requests.get(comment_url)

    if response.status_code == 200:
        comment = response.json()
        return render(request, 'comment/comment.html', {'comment': comment})
    else:
        print(response.json())
        return None


def comments(request):
    comments_url = BASE_API_URL + 'comments/'
    response = requests.get(comments_url)

    if response.status_code == 200:
        comments_list = response.json()
        paginator = Paginator(comments_list, 10)  # Show 10 comments per page.

        page = request.GET.get('page')
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        return render(request, 'comment/comments.html', {'comments': comments})
    else:
        print(response.json())
        return None


def create_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)

        if form.is_valid():
            create_exercise_url = BASE_API_URL + 'exercises/'
            create_exercise_data = json.dumps({
                'courseID': int(form.cleaned_data['course_id']),
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'difficulty': form.cleaned_data['difficulty'],
                'correctAnswer': form.cleaned_data['correct_answer'],
                'firstVariant': form.cleaned_data['first_variant'],
                'secondVariant': form.cleaned_data['second_variant'],
                'thirdVariant': form.cleaned_data['third_variant'],
                'fourthVariant': form.cleaned_data['fourth_variant'],
            })

            print(create_exercise_data)

            response = requests.post(create_exercise_url, data=create_exercise_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('exercises')
            else:
                form.add_error(None, 'Невозможно создать упражнение')
                print(response.json())
                return render(request, 'exercise/create_exercise.html', {'form': form})

    form = ExerciseForm()
    return render(request, 'exercise/create_exercise.html', {'form': form})


def update_exercise(request, exercise_id):
    form = ExerciseForm()

    exercise_url = BASE_API_URL + 'exercises/' + str(exercise_id) + '/'
    response = requests.get(exercise_url)

    if response.status_code == 200:
        exercise = response.json()
        form.fields['course_id'].initial = exercise['course_id']
        form.fields['name'].initial = exercise['name']
        form.fields['description'].initial = exercise['description']
        form.fields['difficulty'].initial = exercise['difficulty']
        form.fields['correct_answer'].initial = exercise['correctAnswer']
        form.fields['first_variant'].initial = exercise['firstVariant']
        form.fields['second_variant'].initial = exercise['secondVariant']
        form.fields['third_variant'].initial = exercise['thirdVariant']
        form.fields['fourth_variant'].initial = exercise['fourthVariant']
    else:
        print(response.json())

    if request.method == 'POST':
        form = ExerciseForm(request.POST)

        if form.is_valid():
            update_exercise_url = BASE_API_URL + 'exercises/' + str(exercise_id) + '/'
            update_exercise_data = {
                'course_id': form.cleaned_data['course_id'],
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'difficulty': form.cleaned_data['difficulty'],
                'correctAnswer': form.cleaned_data['correctAnswer'],
                'fistVariant': form.cleaned_data['first_variant'],
                'secondVariant': form.cleaned_data['second_variant'],
                'thirdVariant': form.cleaned_data['third_variant'],
                'fourthVariant': form.cleaned_data['fourth_variant'],
            }
            response = requests.put(update_exercise_url, data=update_exercise_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('exercises')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно обновить упражнение')
                return render(request, 'exercise/update_exercise.html', {'form': form})

    return render(request, 'exercise/update_exercise.html', {'form': form})


def delete_exercise(request, exercise_id):
    exercise_url = BASE_API_URL + 'exercises/' + str(exercise_id) + '/'
    response = requests.delete(exercise_url)

    if response.status_code == 200:
        return redirect('exercises')
    else:
        print(response.json())
        return None


def get_exercise(request, exercise_id):
    exercise_url = BASE_API_URL + 'exercises/' + str(exercise_id) + '/'
    response = requests.get(exercise_url)

    if response.status_code == 200:
        exercise = response.json()
        return render(request, 'exercise/exercise.html', {'exercise': exercise})
    else:
        print(response.json())
        return None


def exercises(request):
    exercises_url = BASE_API_URL + 'exercises/'
    response = requests.get(exercises_url)

    if response.status_code == 200:
        exercises_list = response.json()
        paginator = Paginator(exercises_list, 10)  # Show 10 exercises per page.

        page = request.GET.get('page')
        try:
            exercises = paginator.page(page)
        except PageNotAnInteger:
            exercises = paginator.page(1)
        except EmptyPage:
            exercises = paginator.page(paginator.num_pages)

        return render(request, 'exercise/exercises.html', {'exercises': exercises})
    else:
        print(response.json())
        return None


def create_lecture(request):
    if request.method == 'POST':
        form = LectureForm(request.POST)

        if form.is_valid():
            create_lecture_url = BASE_API_URL + 'lectures/'
            create_lecture_data = json.dumps({
                'course_id': form.cleaned_data['course_id'],
                'name': form.cleaned_data['name'],
                'content': form.cleaned_data['content']
            })
            response = requests.post(create_lecture_url, data=create_lecture_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('lectures')
            else:
                form.add_error(None, 'Невозможно создать лекцию')
                return render(request, 'lecture/create_lecture.html', {'form': form})

    form = LectureForm()
    return render(request, 'lecture/create_lecture.html', {'form': form})


def update_lecture(request, lecture_id):
    form = LectureForm()

    lecture_url = BASE_API_URL + 'lectures/' + str(lecture_id) + '/'
    response = requests.get(lecture_url)

    if response.status_code == 200:
        lecture = response.json()
        form.fields['course_id'].initial = lecture['course_id']
        form.fields['name'].initial = lecture['name']
        form.fields['description'].initial = lecture['description']
    else:
        print(response.json())

    if request.method == 'POST':
        form = LectureForm(request.POST)

        if form.is_valid():
            update_lecture_url = BASE_API_URL + 'lectures/' + str(lecture_id) + '/'
            update_lecture_data = {
                'course_id': form.cleaned_data['course_id'],
                'name': form.cleaned_data['name'],
                'content': form.cleaned_data['content']
            }
            response = requests.put(update_lecture_url, data=update_lecture_data, headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('lectures')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно обновить лекцию')
                return render(request, 'lecture/update_lecture.html', {'form': form})

    return render(request, 'lecture/update_lecture.html', {'form': form})


def delete_lecture(request, lecture_id):
    lecture_url = BASE_API_URL + 'lectures/' + str(lecture_id) + '/'
    response = requests.delete(lecture_url)

    if response.status_code == 200:
        return redirect('lectures')
    else:
        print(response.json())
        return None


def get_lecture(request, lecture_id):
    lecture_url = BASE_API_URL + 'lectures/' + str(lecture_id) + '/'
    response = requests.get(lecture_url)

    if response.status_code == 200:
        lecture = response.json()
        return render(request, 'lecture/lecture.html', {'lecture': lecture})
    else:
        print(response.json())
        return None


def lectures(request):
    lectures_url = BASE_API_URL + 'lectures/'
    response = requests.get(lectures_url)

    if response.status_code == 200:
        lectures_list = response.json()
        paginator = Paginator(lectures_list, 10)  # Show 10 lectures per page.

        page = request.GET.get('page')
        try:
            lectures = paginator.page(page)
        except PageNotAnInteger:
            lectures = paginator.page(1)
        except EmptyPage:
            lectures = paginator.page(paginator.num_pages)

        return render(request, 'lecture/lectures.html', {'lectures': lectures})
    else:
        print(response.json())
        return None


def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            create_user_url = BASE_API_URL + 'users/signup/'

            avatar = form.cleaned_data['avatar']

            if avatar:
                image = Image.open(avatar)
                image_io = io.BytesIO()
                image.save(image_io, 'PNG')
                image_b64 = base64.b64encode(image_io.getvalue()).decode('utf-8')
                create_user_data = {
                    'login': form.cleaned_data['login'],
                    'email': form.cleaned_data['email'],
                    'role': form.cleaned_data['role'],
                    'password': form.cleaned_data['password'],
                    'avatar': image_b64
                }
            else:
                create_user_data = {
                    'login': form.cleaned_data['login'],
                    'email': form.cleaned_data['email'],
                    'role': form.cleaned_data['role'],
                    'password': form.cleaned_data['password'],
                    'avatar': ''
                }

            response = requests.post(create_user_url, data=json.dumps(create_user_data), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('users')
            else:
                form.add_error(None, 'Невозможно создать пользователя')
                return render(request, 'user/create_user.html', {'form': form})

    form = UserForm()
    return render(request, 'user/create_user.html', {'form': form})


def update_user(request, user_id):
    form = UserForm()

    user_url = BASE_API_URL + 'users/' + str(user_id) + '/'
    response = requests.get(user_url)

    if response.status_code == 200:
        user = response.json()
        form.fields['login'].initial = user['login']
        form.fields['password'].initial = user['password']
        form.fields['email'].initial = user['email']
        form.fields['role'].initial = user['role']
    else:
        print(response.json())

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            update_user_url = BASE_API_URL + 'users/' + str(user_id) + '/'

            avatar = form.cleaned_data['avatar']

            if avatar:
                image = Image.open(avatar)
                image_io = io.BytesIO()
                image.save(image_io, 'PNG')
                image_b64 = base64.b64encode(image_io.getvalue()).decode('utf-8')

                update_user_data = {
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'role': form.cleaned_data['role'],
                    'password': form.cleaned_data['password'],
                    'avatar': image_b64
                }
            else:
                update_user_data = {
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'role': form.cleaned_data['role'],
                    'password': form.cleaned_data['password'],
                    'avatar': ''
                }

            response = requests.put(update_user_url, data=json.dumps(update_user_data), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return redirect('users')
            else:
                print(response.json())
                form.add_error(None, 'Невозможно обновить пользователя')
                return render(request, 'user/update_user.html', {'form': form})

    return render(request, 'user/update_user.html', {'form': form})


def delete_user(request, user_id):
    user_url = BASE_API_URL + 'users/' + str(user_id) + '/'
    response = requests.delete(user_url)

    if response.status_code == 200:
        return redirect('users')
    else:
        print(response.json())
        return None


def get_user(request, user_id):
    user_url = BASE_API_URL + 'users/' + str(user_id) + '/'
    response = requests.get(user_url)

    if response.status_code == 200:
        user = response.json()

        try:
            img = Image.open(io.BytesIO(base64.b64decode(user["avatar"])))
            img.save('media/' + user["login"] + '.png')

            user["avatar"] = MEDIA_URL + user["login"] + '.png'
        except:
            user = {
                "id": user["id"],
                "login": user["login"],
                "email": user["email"],
                "role": user["role"],
                "avatar": MEDIA_URL + "mock.png"
            }

        return render(request, 'user/user.html', {'user': user})
    else:
        print(response.json())
        return None


def users(request):
    users_url = BASE_API_URL + 'users/'
    response = requests.get(users_url)

    if response.status_code == 200:
        users_list = response.json()
        paginator = Paginator(users_list, 10)  # Show 10 users per page.

        page = request.GET.get('page')
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return render(request, 'user/users.html', {'users': users})
    else:
        print(response.json())
        return None

