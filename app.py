import json
import logging
from flask import Flask, render_template, request, jsonify

# Настраиваем логирование API
logging.basicConfig(filename='logs/api.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Создаём Flask-приложение
app = Flask(__name__)

# Пути к файлам данных
POSTS_FILE = "data/data.json"
COMMENTS_FILE = "data/comments.json"
BOOKMARKS_FILE = "data/bookmarks.json"


# Функция загрузки JSON
def load_json(file_path):
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


# Функции получения данных
def get_posts_all():
    return load_json(POSTS_FILE)


def get_comments_all():
    return load_json(COMMENTS_FILE)


def get_posts_by_user(user_name):
    # Загружаем все посты
    posts = get_posts_all()

    # Создаём пустой список для постов пользователя
    user_posts = []

    # Перебираем все посты по одному
    for post in posts:
        # Приводим имя пользователя и автора поста к нижнему регистру и сравниваем
        if post["poster_name"].lower() == user_name.lower():
            user_posts.append(post)  # Если совпало — добавляем пост в список

    # Если в списке user_posts ничего нет, значит, пользователь не найден
    if len(user_posts) == 0:
        raise ValueError("Пользователь не найден")

    # Возвращаем список постов пользователя
    return user_posts


def get_comments_by_post_id(post_id):
    comments = get_comments_all()  # Загружаем все комментарии
    result = []  # Создаём пустой список для нужных комментариев
    for comment in comments:  # Перебираем каждый комментарий
        if comment["post_id"] == post_id:  # Если ID поста совпадает
            result.append(comment)  # Добавляем в список
    return result  # Возвращаем список найденных комментариев


def search_for_posts(query):
    posts = get_posts_all()  # Загружаем все посты
    result = []  # Создаём пустой список для найденных постов
    for post in posts:  # Перебираем все посты
        if query.lower() in post["content"].lower():  # Если слово есть в тексте
            result.append(post)  # Добавляем пост в список
    return result  # Возвращаем список найденных постов


def get_post_by_pk(pk):
    posts = get_posts_all()  # Загружаем все посты
    for post in posts:  # Перебираем каждый пост
        if post["pk"] == pk:  # Если ID совпадает
            return post  # Возвращаем этот пост
    return None  # Если поста нет, возвращаем None


# Маршруты Flask
@app.route('/')
def index():
    posts = get_posts_all()  # Получаем список постов
    return render_template('index.html', posts=posts)  # Передаём в шаблон


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = get_post_by_pk(post_id)  # Получаем пост по ID
    if not post:
        return "Пост не найден", 404
    comments = get_comments_by_post_id(post_id)  # Получаем комментарии к посту
    return render_template('post.html', post=post, comments=comments)


@app.route('/search')
def search():
    query = request.args.get('s', '')
    if not query:
        return render_template('search.html', posts=[], query=query)
    results = search_for_posts(query)[:10]
    return render_template('search.html', posts=results, query=query)


@app.route('/users/<user_name>')
def user_posts(user_name):
    try:
        posts = get_posts_by_user(user_name)
        return render_template('user-feed.html', posts=posts, user_name=user_name)
    except ValueError:
        return "Пользователь не найден", 404


@app.route('/api/posts')
def api_posts():
    logging.info("Запрос /api/posts")
    return jsonify(get_posts_all())


@app.route('/api/posts/<int:post_id>')
def api_post(post_id):
    logging.info(f"Запрос /api/posts/{post_id}")
    post = get_post_by_pk(post_id)
    if not post:
        return jsonify({"error": "Пост не найден"}), 404
    return jsonify(post)


@app.errorhandler(404)
def not_found_error(error):
    return "Страница не найдена", 404


@app.errorhandler(500)
def server_error(error):
    return "Внутренняя ошибка сервера", 500


if __name__ == '__main__':
    import os

    print("\n🔥 Flask запущен! Открой в браузере: http://127.0.0.1:5000/ 🔥\n")
    os.system("python -m flask run --host=127.0.0.1 --port=5000")
