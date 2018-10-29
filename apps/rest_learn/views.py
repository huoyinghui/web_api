from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from rest_learn.models import TestModel
from rest_learn.serializers import UserSerializer, GroupSerializer, TestModelSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TestModeViewSet(viewsets.ModelViewSet):
    """

    """
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
