from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from activities.models import Child
from activities.serializers import ChildSerializer
from authentication.permissions import IsParentUser
from authentication.auth_classes import DerivedUserJWTAuthentication


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, IsParentUser]
    authentication_classes = [DerivedUserJWTAuthentication]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.derived_user)

    def perform_create(self, serializer):
        serializer.save(parent=self.request.derived_user)

    def perform_update(self, serializer):
        if serializer.instance.parent != self.request.derived_user:
            raise PermissionDenied("Cannot modify a child that does not belong to you.")
        
        serializer.save()
