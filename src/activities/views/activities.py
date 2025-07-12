from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone


from activities.models import ActivityInstance, ActivityBooking, ActivitySession
from activities.serializers import ActivityInstanceSerializer, ActivitySessionSerializer
from authentication.permissions import IsParentUser
from authentication.auth_classes import DerivedUserJWTAuthentication
from django.utils.dateparse import parse_datetime

from calendar import monthrange


class ActivityInstancesByUserSocietyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsParentUser]
    authentication_classes = [DerivedUserJWTAuthentication]

    def get(self, request, format=None):
        activity_instances = ActivityInstance.objects.filter(
            society=request.derived_user.society
        ).order_by("start_date")

        serializer = ActivityInstanceSerializer(activity_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetParentUserCalenderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsParentUser]
    authentication_classes = [DerivedUserJWTAuthentication]

    def get(self, request, *args, **kwargs):
        # 1) Find all bookings for this user
        bookings = ActivityBooking.objects.filter(parent_user=request.derived_user)

        # 2) Get all related activity_instance IDs
        activity_instance_ids = bookings.values_list("activity_instance_id", flat=True)

        # 3) Determine the end of the current month
        now = timezone.now()
        last_day_of_month = monthrange(now.year, now.month)[1]
        end_of_month = timezone.make_aware(
            timezone.datetime(year=now.year, month=now.month, day=last_day_of_month, hour=23, minute=59, second=59)
        )

        # 4) Find all sessions in those activity instances until end of the month
        start_after_param = request.query_params.get("start_after")
        if start_after_param:
            start_after = parse_datetime(start_after_param)
            if start_after is None:
                return Response(
                    {"error": "Invalid start_after datetime format. Use ISO 8601."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if timezone.is_naive(start_after):
                start_after = timezone.make_aware(start_after)
        else:
            start_after = now

        sessions = ActivitySession.objects.filter(
            activity_instance_id__in=activity_instance_ids,
            start_date_time__lte=end_of_month,
            start_date_time__gte=now  # Optional: Only future sessions
        ).order_by("start_date_time")

        serializer = ActivitySessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
