# foodgram-project

Дипломный проект курса python-разработчик.
Приложение для размещения и чтения рецептов.
В бэкенд части реализован доступ по api к функциональной части проекта: 
Просмотр существующих записей, добавление собственных рецептов, редактирование,
возможность подписаться на авторов, добавить рецепты в избранное. 
Фильтрация по тегам, избранному, списку покупок, также возможность
скачать список необходимых продуктов в виде файла .txt
Аутентификация и разграничение доступа для различных действий в соответствии с правами пользователей.
Админ часть джанго приложения. 

## Доступ к проекту:

Клонировать репозиторий на свой компьютер 
Перейти в папку infra: cd infra/

Создать .env файл в папке infra, с параметрами:

    DB_NAME=postgres
    POSTGRES_USER=<your postgres_username>
    POSTGRES_PASSWORD=<your postgres_password>
    DB_HOST=db
    DB_PORT=5432

Запустить docker-compose:

```docker-compose up -d```

Выполнить миграции:

```docker-compose exec backend python manage.py migrate```

Собрать staticfiles:

```docker-compose exec backend python manage.py collectstatic --no-input```

Создать пользователя с правами администратора:

```docker-compose exec backend python manage.py createsuperuser```

Удалить contenttypes:

```docker-compose exec backend python manage.py shell ```

В открывшейся консоли вести :

```from django.contrib.contenttypes.models import ContentType```

```ContentType.objects.all().delete()```

```quit()```

Загрузить данные:

```docker-compose exec backend python manage.py loaddata data.json```

На странице http://localhost/api/recipes/ откроется главная страница проекта

Перейти на страницу http://localhost/redoc/ для получения информации обо всех доступных эндпойнтах

Либо на страницу http://localhost/admin для доступа к админ-зоне проекта



Tech_stack:_

__Django 3.2, REST API, ReDoc, Docker__

_Backend author:_

__filimonka https://github.com/filimonka__
