## Yatube

### Описание

Социальная сеть с публикацией постов в общую ленту. Авторы могут подписываться друг на друга. Так же посты можно добавлять в разные группы. Большая часть проекта покрыта тестами.

### Используемые технологии

 - Python 3.7
 - Django
 - Django REST Framework
 - Unittest
 - Pytest

 ### Запуск

 - Клонируйте проект в свою рабочую директорию на компьютере
```html
    git clone/<путь репозитория>
```
  - Перейдите в директорию с проектом
```html
    ls <путь до директории>
```
  - Создать и активировать виртуальное окружение

```html
    python3 -m venv venv
```
```html
    source/venv/bin/activate
```
  - Устанавливаем зависимости
```html
    pip install -r requirements.txt 
```
- Собираем статические файлы
```html
    python manage.py collectstatic
```
  - Выполняем миграции
```html
    python manage.py migrate 
```
  - Запускаем сервер
```html
    python manage.py runserver
```

### Тесты

 Запускаем тесты
```html
    python manage.py test
```

### Автор
  Солилов Александр

