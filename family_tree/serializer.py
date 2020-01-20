from rest_framework import serializers

from family_tree.models import People, Connection


class ConnectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Connection
        fields = "__all__"


class PeopleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = People
        fields = "__all__"


