from rest_framework.permissions import BasePermission

class IsOwnerOrBusinessMember(BasePermission):
    """
    Custom permission to only allow owners or business members to access an object.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Direct owner (personal)
        if hasattr(obj, 'personal_user') and obj.personal_user == user:
            return True
        # Business member
        if hasattr(obj, 'business') and obj.business:
            return obj.business.members.filter(user=user).exists()
        return False
