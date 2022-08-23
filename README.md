# foodgram-project

Дипломный проект курса python-разработчик.
Приложение для размещения и чтения рецептов.

## Для запуска проекта:

Клонировать репозиторий на свой компьютер
https://github.com/filimonka/infra_sp2

Перейти в папку infra:
```cd infra/```

Создать .env файл в папке infra, с параметрами:
``` DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=<your postgres_username>
    POSTGRES_PASSWORD=<your postgres_password>
    DB_HOST=db
    DB_PORT=5432
```
Запустить docker-compose:

```docker-compose up -d```

Выполнить миграции:

```docker-compose exec web python manage.py migrate```

Собрать staticfiles:

```docker-compose exec web python manage.py collectstatic --no-input```

Создать пользователя с правами администратора:

```docker-compose exec web python manage.py createsuperuser```

Загрузить данные:

```docker-compose exec web python manage.py loaddata data.json```

Перейти на страницу http://localhost/api/users для создания учетной записи.
Важно запомнить введенный пароль, аутентификация происходит по email и паролю

Админ часть проекта откроется по адресу http://localhost/admin/

Tech_stack:_

__Django 3.2, REST API, ReDoc, Docker__

_Author:_

__filimonka https://github.com/filimonka__