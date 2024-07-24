# Сервис "Блог"
---

# Описание

Сервис "Блог" позволяет создавать посты и читать чужие. Для написания поста пользователь должен зарегистрироваться и пройти аутентификацию. Посты могут быть с отложенной публикацией, можно прикладывать картинки к ним. Также доступно комментирование.

# Как запустить сервис

Клонировать репозиторий

```
git clone git@github.com:AlehAkbashev/Blog.git
```

Установить локальное окружение

```
python3 -m venv venv
```

Активировать локальное окружение

```
source venv/bin/activate
```

Установить все зависимости из файла requirements.txt

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции

```
python manage.py makemigrations
```
```
python manage.py migrate
```

Запустить сервер

```
python manage.py runserver
```
