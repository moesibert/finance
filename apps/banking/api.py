from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status

from apps.banking.serializers import AccountSerializer, ChangeSerializer, CategorySerializer, DepotSerializer
from apps.banking.permissions import IsOwner
from apps.banking.models import Account, Change, Category, Depot

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView


class DepotViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows depots to be viewed or edited.
    """
    serializer_class = DepotSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Depot.objects.none()

    def get_queryset(self):
        return Depot.get_objects_by_user(self.request.user)


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows accounts to be viewed or edited.
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Account.objects.none()

    def get_queryset(self):
        return Account.get_objects_by_user(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.changes.exists():
            return Response(data={'message': "You can't delete an account that contains changes"},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Category.objects.none()

    def get_queryset(self):
        return Category.get_objects_by_user(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.changes.exists():
            return Response(data={'message': "You can't delete a category that contains changes"},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows changes to be viewed or edited.
    """
    serializer_class = ChangeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Change.objects.none()

    def get_queryset(self):
        return Change.get_objects_by_user(self.request.user)


# chart api
class IncomeAndExpenditureData(GenericAPIView):
    def get_queryset(self):
        user = self.request.user
        return user.banking_depots.all()

    def get(self, request, pk):
        instance = self.get_object()

        data = instance.get_income_and_expenditure_data()

        return Response(data)


class BalanceData(GenericAPIView):
    def get_queryset(self):
        user = self.request.user
        return user.banking_depots.all()

    def get(self, request, pk):
        instance = self.get_object()

        data = instance.get_balance_data()

        return Response(data)