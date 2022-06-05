from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from apps.users.api.serializers import UserSerializer, UserListSerializer

class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer

    def get_object(self, pk):
        # return self.serializer_class().Meta.model.objects.filter(id=pk).first()
        return get_object_or_404(self.serializer_class().Meta.model, pk=pk)

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.serializer_class().Meta.model\
                                .objects.filter(is_active=True)\
                                .values('id', 'username', 'email', 'name')
        return self.queryset

    def list(self, request):
        users = self.get_queryset()
        users_serializer = self.list_serializer_class(users, many=True)
        return Response(users_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = self.get_object(pk)
        user_serializer = self.serializer_class(user)
        return Response(user_serializer.data)
