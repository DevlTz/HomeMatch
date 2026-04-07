from rest_framework import permissions

class IsAdvertiser(permissions.BasePermission):
    message = "You do not have permission to do this action. Please, change your account type to advertise!"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.user_type == "A"
        )

class IsReviewOwner(permissions.BasePermission):
    message = "You only can edit or delete your own reviews."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsPropertyOwner(permissions.BasePermission):
    message = "You do not have permission to do this action."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "property"):
            return obj.property.owner == request.user
        return False