from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.models import CustomUser, ParentUser, InstructorUser
from backend_main.utils.orm_utils import try_get_object_by_unique_field


class DerivedUserJWTAuthentication(JWTAuthentication):
    """
    Subclass of JWTAuthentication that attaches request.derived_user.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            # No authentication provided
            return None

        user, validated_token = result

        derived_user = None
        if user.user_type == CustomUser.USER_TYPE_PARENT:
            derived_user = try_get_object_by_unique_field(ParentUser, "user", user)
        elif user.user_type == CustomUser.USER_TYPE_INSTRUCTOR:
            derived_user = try_get_object_by_unique_field(InstructorUser, "user", user)
        # else: leave derived_user as None

        # Attach derived_user to request
        request.derived_user = derived_user

        return (user, validated_token)
