from rest_framework import permissions


class IsNotAuthor(permissions.BasePermission):
    message = 'Подписка на самого себя невозможна'

    def has_permission(self, request, view):
        author_id = request.resolver_match.kwargs.get('id')
        return request.user.id != int(author_id)


class PutForbidden(permissions.BasePermission):
    message = 'Метод "PUT" запрещен, используйте "PATCH"'

    def has_permission(self, request, view):
        if request.method == 'PUT':
            return False
        return True


class UpdateForbidden(permissions.BasePermission):
    message = 'Редактирование данных User запрещено'

    def has_permission(self, request, view):
        if request.method in ('PUT', 'PATCH'):
            return False
        return True
