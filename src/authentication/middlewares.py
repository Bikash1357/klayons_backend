from authentication.models import CustomUser, ParentUser, InstructorUser
from backend_main.utils.orm_utils import try_get_object_by_unique_field


class DerivedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user or not request.user.is_authenticated:
            return self.get_response(request)

        user_type = request.user.user_type
        
        derived_user = None
        if user_type == CustomUser.USER_TYPE_PARENT:
            derived_user = try_get_object_by_unique_field(ParentUser, "user", request.user)            
        elif user_type == CustomUser.USER_TYPE_INSTRUCTOR:
            derived_user = try_get_object_by_unique_field(InstructorUser, "user", request.user)
        else:
            pass
        request.derived_user = derived_user
        
        return self.get_response(request)
