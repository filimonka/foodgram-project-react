from urllib import request
import pytest
from django.contrib.auth import get_user_model

User = get_user_model


class TestUser:
    url_get_post = '/api/users/'
    url_get_token = '/api/auth/token/login/'
    url_del_token = '/api/auth/token/logout/'
    url_set_password = '/api/users/set_password/'

    @pytest.mark.django_db(transaction=True)
    def test_user_create__invalid_request_data(self, client, user):
        url = self.url_get_post
        response = client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        fields_invalid = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код {code_expected} с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )
        
        invalid_data = {
            'email': 'str',
            'username': 'qwerty@-',
            'first_name': '@@@',
            'last_name': '',
            'password': '//f2@'
        }
        response = client.post(url, invalid_data)
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        fields_invalid = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код {code_expected} с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )
 
    @pytest.mark.django_db(transaction=True)
    def test_user_create__valid_request_data(self, client, user):
        url = self.url_create
        valid_data = {
            'email': 'unique@any.com',
            'username': 'unicum',
            'first_name': 'Коля',
            'last_name': 'Иванов',
            'password': '1234567'
        }
        response = client.post(url, data=valid_data)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` с валидными данными, '
            f'возвращается код {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_user_get_users(self, client, user):
        url = self.url_get_post
        url = f'{url}?limit={limit}&offset={offset}'
        limit = 2
        offset = 2
        response = client.get(url)
        assert response.status_code != 404, (
            f'Страница {url} не найдена, проверьте этот адрес в *urls.py*'
        )
        code_expected = 200
        assert response.status == code_expected, (
            f'Убедитесь, что при запросе `{url}`'
            f'возвращается код {code_expected}'
        )
        test_data = response.json()
        assert type(test_data) == dict, (
            f'Убедитесь, что при запросе `{url}`'
            'возвращаете словарь'
        )
        assert 'results' in test_data.keys(), (
            f'Убедитесь, что при GET запросе на `{url}` с пагинацией, ключ `results` присутствует в ответе'
        )
        test_user = test_data.get('results')[0]
        assert 'id' in test_user, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели User'
        )
        assert 'email' in test_user, (
            'Проверьте, что добавили `email` в список полей `fields` сериализатора модели User'
        )
        assert 'username' in test_user, (
            'Проверьте, что добавили `username` в список полей `fields` сериализатора модели User'
        )
        assert 'first_name' in test_user, (
            'Проверьте, что добавили `first_name` в список полей `fields` сериализатора модели User'
        )
        assert 'last_name' in test_user, (
            'Проверьте, что добавили `last_name` в список полей `fields` сериализатора модели User'
        )
        assert 'is_subscribed' in test_user, (
            'Проверьте, что добавили `is_subscribed` в список полей `fields` сериализатора модели User'
        )

    @pytest.mark.django_db(transaction=True)
    def test_get_exact_user(self, user_client, user):
        response = user_client.get(f'/api/users/{id}/')

        assert response.status_code == 200, (
            'Страница `/api/users/{id}/` не найдена,'
            'либо учетные данные не предоставлены'
        )

        test_data = response.json()

        assert test_data.get('id') == user.id, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `id`'
        )
        assert test_data.get('email') == user.email, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `email`'
        )
        assert test_data.get('username') == user.username, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `username`'
        )
        assert test_data.get('first_name') == user.first_name, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `first_name`'
        )
        assert test_data.get('last_name') == user.last_name, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `last_name`'
        )
        assert test_data.get('is_subscribed') == user.is_subscribed, (
            'Проверьте, что при GET запросе `/api/users/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `is_subscribed`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_get_current_user(self, user_client):
        current_user = request.user
        response = current_user.get('/api/users/me/')
        assert response.status_code == 200, (
            'Проверьте переданные учетные данные' 
        )
    
    @pytest.mark.django_db(transaction=True)
    def test_user_change_password_invalid_and_valid_data(self, client):
        url = self.url_set_password
        test_user = User.objects.create(
            data={
                'email': 'unique@example.com',
                'username': 'melofon',
                'first_name': 'Коля',
                'last_name': 'Герасимов',
                'password': '1234567',
                }
            )
        response = test_user.post(url)
        fields_invalid = ['new_password', 'current_password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код 400 с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )

        data_invalid = {
            'new_password': '12345678',
            'current_password': '222'
        }

        response = test_user.post(url, data_invalid)
        fields_invalid = ['new_password', 'current_password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` с неверными данными, '
                f'возвращается код 400 с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )
        data_valid = {
            'new_password': '12345678',
            'current_password': '1234567'
        }
        response == test_user.post(url, data_valid)
        assert response.status_code == 204, (
            'Проверьте, что при запросе смены пароля авторизованным пользователем'
            'возвращаете ответ 204'
        )
    
    @pytest.mark.django_db(transaction=True)
    def test_user_obtain_token(self):
        url = self.url_get_token
        test_user = User.objects.create(
            data={
                'email': 'unique@example.com',
                'username': 'melofon',
                'first_name': 'Коля',
                'last_name': 'Герасимов',
                'password': '1234567',
                }
            )
        response = test_user.post(url)
        fields_invalid = ['email', 'password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код 400 с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )
        
        invalid_data = {
            'email': 'example@example.com',
            'password': '123'
        }
        response = test_user.post(url, invalid_data)
        fields_invalid = ['email', 'password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` с неверными данными, '
                f'возвращается код 400 с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'{field}: обязательное поле'
            )
        
        valid_data = {
            'email': 'unique@example.com',
            'password': '1234567'
        }
        response = test_user.post(url, valid_data)
        assert response.status_code == 201(
            'Проверьте, что при получения токена с правильными данными'
            'возвращаете код 201'
        )
        assert type(response.json()) == dict(
            'Проверьте, что при запросе токена с правильными данными'
            'формат данных ответа словарь'
        )
        assert 'auth_token' in response.json().keys(),(
            'Проверьте, что при запросе токена возвращается ключ `auth_token`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_user_delete_token(self):
        url = self.url_del_token
        test_user = User.objects.create(
            data={
                'email': 'unique@example.com',
                'username': 'melofon',
                'first_name': 'Коля',
                'last_name': 'Герасимов',
                'password': '1234567',
                }
            )
        test_user.post(
            self.url_get_token,
            data={
                'email': 'unique@example.com',
                'password': '1234567',
            }
        )
        response = test_user.post(url)
        assert response.status_code == 204, (
            'Проверьте, что авторизованный пользователь может удалить свой токен'
        )
        