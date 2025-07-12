from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    List notifications for the authenticated user with custom pagination.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Validate query params
        entries_per_page = request.query_params.get('entries_per_page')
        page_num = request.query_params.get('page_num')

        if entries_per_page is None or page_num is None:
            return Response(
                {"detail": "Both 'entries_per_page' and 'page_num' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            entries_per_page = int(entries_per_page)
            page_num = int(page_num)
        except ValueError:
            return Response(
                {"detail": "'entries_per_page' and 'page_num' must be integers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if entries_per_page < 1 or entries_per_page > 100:
            return Response(
                {"detail": "'entries_per_page' must be between 1 and 100."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if page_num < 1:
            return Response(
                {"detail": "'page_num' must be >= 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch notifications
        queryset = Notification.objects.filter(base_user=request.user).order_by('-created_at')

        # Calculate pagination
        start = (page_num - 1) * entries_per_page
        end = start + entries_per_page

        total_entries = queryset.count()
        paginated_queryset = queryset[start:end]
        serializer = NotificationSerializer(paginated_queryset, many=True)

        return Response({
            "total_entries": total_entries,
            "page_num": page_num,
            "entries_per_page": entries_per_page,
            "results": serializer.data
        })


class NotificationMarkAsReadView(APIView):
    """
    Mark a single notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, base_user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        if notification.is_read:
            return Response({"detail": "Notification already marked as read."}, status=status.HTTP_200_OK)

        notification.is_read = True
        notification.save()

        return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)
