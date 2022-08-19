import pytest

class TestTagsAndIngredients:
    
    @pytest.mark.django_db(transaction=True)
    def test_get_tags_or_ingredients(self, client):
        url_tags = '/api/tags/'
        url_ingredients = '/api/ingredients/'
        response = client.get(url_tags)
        second_response = client.get(url_ingredients)
        assert response.status_code == 200, (
            f'Страница {url_tags} не найдена, проверьте urls.py'
        )
        assert second_response.status_code == 200, (
            f'Страница {url_ingredients} не найдена, проверьте urls.py'
        )
        assert type(response) == dict, (
            f'Проверьте, что при запросе на {url_tags}'
            'возвращаете данные в формате json'
        )
        assert type(second_response) == dict, (
            f'Проверьте, что при запросе на {url_ingredients}'
            'возвращаете данные в формате json'
        )

        test_tag = response.json()[0]
        assert 'id' in test_tag.keys(), (
            f'Проверьте, что ключ `id` содержится в ответе {url_tags}'
        )
        assert 'name' in test_tag.keys(), (
            f'Проверьте, что ключ `name` содержится в ответе {url_tags}'
        )
        assert 'color' in test_tag.keys(), (
            f'Проверьте, что ключ `color` содержится в ответе {url_tags}'
        )
        assert 'slug' in test_tag.keys(), (
            f'Проверьте, что ключ `slug` содержится в ответе {url_tags}'
        )
        assert test_tag.get('color') == '^#/w{6}', (
            f'Проверьте, что передаете значение цвета в Hex-формате {url_tags}'
        )

        test_ingredient = second_response.json()[0]
        assert 'id' in test_ingredient.keys(), (
            f'Проверьте, что ключ `id` содержится в ответе {url_ingredients}'
        )
        assert 'name' in test_ingredient.keys(), (
            f'Проверьте, что ключ `name` содержится в ответе {url_ingredients}'
        )
        assert 'measurement_unit' in test_ingredient.keys(), (
            f'Проверьте, что ключ `measurement_unit` содержится в ответе {url_ingredients}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_get_current_tag_or_ingredient(self, client, tag, ingredient):
        url_tag = f'/api/tags/{tag.id}/'
        url_ingredient = f'/api/ingredients/{ingredient.id}/'
        response_tag = client.get(url_tag)
        response_ingredient = client.get(url_ingredient)
        assert response_tag.status_code != 400, (
            f'Проверьте, что страница {url_tag} существует'
        )
        assert response_ingredient.status_code != 400, (
            f'Проверьте, что страница {url_ingredient} существует'
        )
        test_tag = response_tag.json()
        test_ingredient = response_ingredient.json()
        assert type(test_tag) == dict, (
            f'Проверьте, что ответ {url_tag} возвращается в формате json'
        )
        assert type(test_ingredient) == dict, (
            f'Проверьте, что ответ {url_ingredient} возвращается в формате json'
        )
