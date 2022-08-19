from rest_framework import permissions

class IsNotAuthor(permissions.BasePermission):
    message = 'Подписка на самого себя невозможна'
    def has_permission(self, request, view):
        author_id = request.resolver_match.kwargs.get('id')
        return request.user.id != int(author_id)