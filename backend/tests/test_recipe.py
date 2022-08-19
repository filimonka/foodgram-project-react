import pytest

from recipe.models import Recipe

class TestRecipeApi:

    @pytest.mark.django_db(transaction=True)
    def test_recipe_not_found(self, client, recipe):
        response = client.get('/api/recipes/')

        assert response.status_code != 404, (
             'Страница "/api/recipes/" не найдена, проверьте этот адрес в *urls.py*'
        )
    
    @pytest.mark.django_db(transaction=True)
    def test_post_list_not_auth(self, client, ):
        response = client.get('/api/recipes/')

        assert response.status_code == 200, (
            'Проверьте, что на "/api/recipes/" при запросе без токена возвращаете статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_single_not_auth(self, client, recipe):
        response = client.get(f'/api/recipes/{id}/')

        assert response.status_code == 200, (
            'Проверьте, что на "/api/recipes/{id}/" при запросе без токена возвращаете статус 200'
        )
    
    @pytest.mark.django_db(transaction=True)
    def test_posts_get_paginated(self, user_client, recipe, recipe_2, another_recipe):
        base_url = '/api/recipes/'
        limit = 2
        offset = 2
        url = f'{base_url}?limit={limit}&offset={offset}'
        response = user_client.get(url)
        assert response.status_code == 200, (
            f'Проверьте, что при GET запросе `{url}` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()

        # response with pagination must be a dict type
        assert type(test_data) == dict, (
            f'Проверьте, что при GET запросе на `{url}` с пагинацией, возвращается словарь'
        )
        assert 'results' in test_data.keys(), (
            f'Убедитесь, что при GET запросе на `{url}` с пагинацией, ключ `results` присутствует в ответе'
        )
        assert len(test_data.get('results')) == Recipe.objects.count() - offset, (
            f'Проверьте, что при GET запросе на `{url}` с пагинацией, возвращается корректное количество статей'
        )
        assert test_data.get('results')[0].get('text') == another_recipe.text, (
            f'Убедитесь, что при GET запросе на `{url}` с пагинацией, '
            'в ответе содержатся корректные рецепты'
        )
        recipe = Recipe.objects.get(text=another_recipe.text)
        test_recipe = test_data.get('results')[0]
        assert 'id' in test_recipe, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Recipe'
        )
        assert 'text' in test_recipe, (
            'Проверьте, что добавили `text` в список полей `fields` сериализатора модели Recipe'
        )
        assert 'author' in test_recipe, (
            'Проверьте, что добавили `author` в список полей `fields` сериализатора модели Recipe'
        )
        assert 'tags' in test_recipe, (
            'Проверьте, что добавили "tags" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'ingredients' in test_recipe(
            'Проверьте, что добавили "ingredients" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'is_favorited' in test_recipe, (
            'Проверьте, что добавили "is_favorited" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'is_in_shopping_cart' in test_recipe, (
            'Проверьте, что добавили "is_in_shopping_cart" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'name' in test_recipe, (
            'Проверьте, что добавили "name" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'image' in test_recipe, (
            'Проверьте, что добавили "image" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'text' in test_recipe, (
            'Проверьте, что добавили "text" в список полей `fields` сериализатора модели Recipe'
        )
        assert 'cooking_time' in test_recipe, (
            'Проверьте, что добавили `cooking_time` в список полей `fields` сериализатора модели Recipe'
        )
        assert test_recipe['id'] == recipe.id, (
            'Проверьте, что при GET запросе на `{url}` возвращается корректный список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipe_create(self, user_client, user, another_user):
        user = user
        recipe_count = Recipe.objects.count()
        data = {}
        response = user_client.post('/api/recipes/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/recipes/`  с не правильными данными возвращается статус 400'
        )

        data = {
            "ingredients": [
                {
                "id": 1123,
                "amount": 10
                }
            ],
            "tags": [
                1,
                2
                ],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "Колбаса",
            "text": "Коптить или вырить, вот в чём вопрос",
            "cooking_time": 1
        }
        response = user_client.post('/api/recipes/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/recipes/` с правильными данными возвращается статус 201'
        )
        assert (
                response.json().get('author') is not None
                and response.json().get('author') == user_client
        ), (
            'Проверьте, что при POST запросе на `/api/recipes/` автором указывается пользователь,'
            'от имени которого сделан запрос'
        )
        test_data = response.json()
        msg_error = (
            'Проверьте, что при POST запросе на `/api/recipes/` возвращается словарь с данными нового рецепта'
        )
        assert type(test_data) == dict, msg_error
        assert type(test_data.get('ingredients')) == dict, msg_error
        assert type(test_data.get('tags')) == dict, msg_error
        assert test_data.get('text') == data['text'], msg_error
        assert test_data.get('cooking_time') == data['cooking_time'], msg_error
        assert test_data.get('name') == data['name'], msg_error
        assert test_data.get('image') == data['image'], msg_error
        assert recipe_count + 1 == Recipe.object.count(), msg_error


    @pytest.mark.django_db(transaction=True)
    def test_recipe_get_current(self, user_client, recipe, user):
        response = user_client.get(f'/api/recipes/{id}/')

        assert response.status_code == 200, (
            'Страница `/api/recipes/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )

        test_data = response.json()

        assert test_data.get('text') == recipe.text, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `text`'
        )
        assert test_data.get('author') == user (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `author`, должно возвращать словарь пользователя  со всеми полями'
        )
        assert test_data.get('id') == recipe.id, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `id`'
        )
        assert test_data.get('tags') == recipe.id, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `tags`'
        )
        assert test_data.get('tags') == recipe.tags, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `tags`'
        )
        assert test_data.get('ingredients') == recipe.ingredients, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `ingredients`'
        )
        assert test_data.get('is_favorited') == recipe.is_favorited, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `is_favorited`'
        )
        assert test_data.get('is_in_shopping_cart') == recipe.is_in_shopping_cart, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `is_in_shopping_cart`'
        )
        assert test_data.get('name') == recipe.name, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `name`'
        )
        assert test_data.get('image') == recipe.image, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `image`'
        )
        assert test_data.get('cooking_time') == recipe.cooking_time, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `cooking_time`'
        )
        assert test_data.get('is_in_shopping_cart') == recipe.is_in_shopping_cart, (
            'Проверьте, что при GET запросе `/api/recipes/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `is_in_shopping_cart`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipe_patch_current(self, user_client, recipe, another_recipe):
        response = user_client.patch(f'/api/recipes/{recipe.id}/',
                                     data={'text': 'Поменяли текст рецепта'})

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/` возвращаете статус 200'
        )

        test_recipe = Recipe.objects.filter(id=recipe.id).first()

        assert test_recipe, (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/` вы не удалили рецепт'
        )

        assert test_recipe.text == 'Поменяли текст статьи', (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/` вы изменяете рецепт'
        )

        response = user_client.patch(f'/api/recipes/{another_recipe.id}/',
                                     data={'text': 'Поменяли текст рецепта'})

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/recipes/{id}/` для не своей статьи возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipe_delete_current(self, user_client, recipe, another_recipe):
        response = user_client.delete(f'/api/v1/posts/{recipe.id}/')

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/recipes/{id}/` возвращаете статус 204'
        )

        test_recipe = Recipe.objects.filter(id=recipe.id).first()

        assert not test_recipe, (
            'Проверьте, что при DELETE запросе `/api/recipes/{id}/` вы удалили статью'
        )

        response = user_client.delete(f'/api/v1/posts/{another_recipe.id}/')

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/recipes/{id}/` для не своей статьи возвращаете статус 403'
        )

