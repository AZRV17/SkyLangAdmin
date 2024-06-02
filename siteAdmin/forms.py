from django import forms
import requests

BASE_API_URL = 'http://127.0.0.1:8080/'

class LoginForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=255)
    password = forms.CharField(label="Пароль", max_length=255, widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=255, widget=forms.TextInput)
    password = forms.CharField(label="Пароль", max_length=255, widget=forms.PasswordInput)
    email = forms.EmailField(label="Email", widget=forms.EmailInput)
    role = forms.CharField(label="Роль", max_length=255)


def get_users():
    users_url = BASE_API_URL + 'users/'

    response = requests.get(users_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_courses():
    courses_url = BASE_API_URL + 'courses/'

    response = requests.get(courses_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_exercises():
    exercises_url = BASE_API_URL + 'exercises/'

    response = requests.get(exercises_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_lectures():
    lectures_url = BASE_API_URL + 'lectures/'

    response = requests.get(lectures_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_comments():
    comments_url = BASE_API_URL + 'comments/'

    response = requests.get(comments_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


class CourseForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название")
    description = forms.CharField(widget=forms.Textarea, label="Описание")
    language = forms.CharField(max_length=50, label="Язык")
    icon = forms.ImageField(label="Иконка", required=False, help_text="Минимальное разрешение: 200x200")
    rating = forms.IntegerField(label="Рейтинг", required=False)
    author_id = forms.ChoiceField(label="ID Автора")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = get_users()
        if users:
            user_choices = [(user['id'], user['login']) for user in users]
        else:
            user_choices = [('', 'No users available')]
        self.fields['author_id'].choices = user_choices


class CommentForm(forms.Form):
    course_id = forms.ChoiceField(label="ID Курса")
    author_id = forms.ChoiceField(label="ID Автора")
    content = forms.CharField(widget=forms.Textarea, label="Содержание")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        courses = get_courses()
        if courses:
            course_choices = [(course['id'], course['name']) for course in courses]
        else:
            course_choices = [('', 'No courses available')]
        self.fields['course_id'].choices = course_choices

        users = get_users()
        if users:
            user_choices = [(user['id'], user['login']) for user in users]
        else:
            user_choices = [('', 'No users available')]
        self.fields['author_id'].choices = user_choices


class ExerciseForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название")
    description = forms.CharField(widget=forms.Textarea, label="Описание")
    first_variant = forms.CharField(max_length=255, label="Первый вариант")
    second_variant = forms.CharField(max_length=255, label="Второй вариант")
    third_variant = forms.CharField(max_length=255, label="Третий вариант")
    fourth_variant = forms.CharField(max_length=255, label="Четвертый вариант")
    correct_answer = forms.CharField(max_length=255, label="Правильный ответ")
    difficulty = forms.CharField(max_length=50, label="Сложность")
    course_id = forms.ChoiceField(label="ID Курса")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        courses = get_courses()
        if courses:
            course_choices = [(course['id'], course['name']) for course in courses]
        else:
            course_choices = [('', 'No courses available')]
        self.fields['course_id'].choices = course_choices


class LectureForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название")
    description = forms.CharField(widget=forms.Textarea, label="Описание")
    course_id = forms.ChoiceField(label="ID Курса")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        courses = get_courses()
        if courses:
            course_choices = [(course['id'], course['name']) for course in courses]
        else:
            course_choices = [('', 'No courses available')]
        self.fields['course_id'].choices = course_choices


class UserForm(forms.Form):
    login = forms.CharField(max_length=255, label="Логин")
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Пароль")
    email = forms.EmailField(label="Email")
    role = forms.CharField(max_length=50, label="Роль")
    avatar = forms.ImageField(required=False, label="Аватар")
