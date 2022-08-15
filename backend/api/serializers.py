from rest_framework.serializers import ModelSerializer
from .models import BooksToSearch


class BooksToSearchSerializer(ModelSerializer):
    class Meta:
        model = BooksToSearch
        fields = '__all__'
