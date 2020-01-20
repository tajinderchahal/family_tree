from django.db.models import Q

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import People, Connection
from .serializer import PeopleSerializer

# Create your views here.

class PeopleViewSet(ModelViewSet):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer

    @action(detail=True, methods=['get'])
    def get_connection(self, request, *args, **kwargs):
        person = self.get_object()
        relation_type = request.query_params.get('relation_type', None)
        if not relation_type:
            raise serializers.ValidationError({"error": 'relation_type is required field'})


        if relation_type == "cousin":
            parents = Connection.objects.filter(relation_type="parent", related_person=person).values_list('people_id', flat=True)
            parents_sliblings = Connection.objects.filter(relation_type="sibling", related_person_id__in=parents).values_list('people_id', flat=True)
            connected_people_id = Connection.objects.filter(relation_type="children", related_person_id__in=parents_sliblings).values_list('people_id', flat=True)
            
        elif relation_type == "grand_parent":
            parents = Connection.objects.filter(relation_type="parent", related_person=person).values_list('people_id', flat=True)
            connected_people_id = Connection.objects.filter(relation_type="parent", related_person_id__in=parents).values_list('people_id', flat=True)
        else:
            connected_people_id = list(Connection.objects.filter(relation_type=relation_type, related_person=person).values_list('people_id', flat=True))

        return Response(PeopleSerializer(People.objects.filter(id__in=connected_people_id).exclude(id=person.id), many=True).data)


