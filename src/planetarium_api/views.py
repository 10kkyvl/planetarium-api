from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from planetarium_api.models import ShowSession
from planetarium_api.serializers import (
    RegisterSerializer,
    ShowSessionSerializer
)


class RegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names = ["post"]


class ShowsViewSet(ModelViewSet):
    def list(self, request):
        queryset = ShowSession.objects.all()
        serializer = ShowSessionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        show_session = get_object_or_404(ShowSession, id=pk)
        serializer = ShowSessionSerializer(show_session)
        return Response(serializer.data)
