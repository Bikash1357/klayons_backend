from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from authentication.models import ParentUser, InstructorUser


class IsParentUser(BasePermission):
    def has_permission(self, request, view):
        if not request.derived_user or not isinstance(request.derived_user, ParentUser):
            raise PermissionDenied("Only Parent users can access this resource.")
        
        return True


class IsInstructorUser(BasePermission):
    def has_permission(self, request, view):
        if not request.derived_user or not isinstance(request.derived_user, InstructorUser):
            raise PermissionDenied("Only Instructor users can access this resource.")
        
        return True
