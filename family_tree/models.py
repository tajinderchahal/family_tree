from django.db import models
from rest_framework import serializers
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class People(models.Model):
    GENDER_CHOICE = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others')
    )
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=25, null=True, blank=True)
    phone_numner = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, choices=GENDER_CHOICE)
    relations = models.ManyToManyField('self', through='Connection', symmetrical=False)

    def __str__(self):
        return "{} {}".format(self.first_name or "", self.last_name or "")

    @property
    def get_full_name(self):
        return "{} {}".format(self.first_name or "", self.last_name or "")

    def get_direct_parents(self):
        return list(Connection.objects.filter(relation_type='parent', related_person=self).values_list('people_id', flat=True))

    def get_direct_siblings(self):
        return list(Connection.objects.filter(relation_type='sibling', related_person=self).values_list('people_id', flat=True))

    def get_siblings(self):
        my_parents = self.get_direct_parents()
        my_parents_children = list(Connection.objects.filter(relation_type='children', related_person__in=my_parents).values_list('people_id', flat=True))
        my_direct_siblings = self.get_direct_siblings()
        return my_parents_children + my_direct_siblings

    def get_parents(self):
        my_direct_parents = self.get_direct_parents()
        my_direct_siblings = self.get_direct_siblings()
        my_indirect_siblings = list(Connection.objects.filter(relation_type='children', related_person__in=my_direct_parents).values_list('people_id', flat=True)) 
        my_siblings_parents = list(Connection.objects.filter(relation_type='parent', related_person__in=(my_direct_siblings + my_indirect_siblings)).values_list('people_id', flat=True))
        return my_direct_parents + my_siblings_parents

  
class Connection(models.Model):
    RELATION_CHOICES = (
        ('grand_parent', 'Grand Parent of'),
        ('parent', 'Parent of'),
        ('children', 'Child of'),
        ('sibling', 'Sibling of'),
        ('cousin', 'Cousin of'),
        ('spouse', 'Spouse of')
    )

    RELATION_REVERSE_MAPPING = {
        "parent": "children",
        "children": "parent",
        "sibling": "sibling",
        "cousin": "cousin",
        "spouse": "spouse"
    }

    people = models.ForeignKey(People, on_delete=models.CASCADE, related_name="actor")
    relation_type = models.CharField(max_length=20, null=True, blank=True, choices=RELATION_CHOICES)
    related_person = models.ForeignKey(People, on_delete=models.CASCADE, related_name="related_person")

    def __str__(self):
        return "{} is {} of {}".format(self.people.get_full_name, self.relation_type, self.related_person.get_full_name)

    def clean(self):
        if self.relation_type == "parent":
            # check if the parent i.e. (self.people) has a spouse if not then can't have a child (adoption not allowed)
            if not Connection.objects.filter(relation_type="spouse", people=self.people).exists():
                raise ValidationError(_('Can\'t have a child because "{}" doesn\'t have a spouse (single parent not allowed)'.format(self.people.get_full_name)))

        if self.relation_type == "sibling":
            # i can have a sibling only if i have parents
            if not Connection.objects.filter(relation_type="children", people=self.people).exists():
                raise ValidationError(_('Can\'t have a sibling because {} don\'t have parents'.format(self.people.get_full_name)))

        if self.relation_type == "children":
            # can't have a child if you don't have a spouse
            if not Connection.objects.filter(relation_type="spouse", people=self.related_person).exists():
                name = self.related_person.get_full_name
                raise ValidationError(_('Can\'t be a child of "{}" because "{}" don\'t have a spouse (single parent not allowed)'.format(name, name)))

        if self.relation_type == "spouse":
            # can't have more than one spouse
            if Connection.objects.filter(relation_type="spouse", people=self.people).exists():
                raise ValidationError(_('{} is already have a spouse. Can\'t have more than one spouse'.format(self.people.get_full_name)))
            elif Connection.objects.filter(relation_type="spouse", people=self.related_person).exists():
                raise ValidationError(_('{} is someone else\'s spouse. Can\'t be a spouse of someone else\'s spouse'.format(self.related_person.get_full_name)))

        if self.relation_type in ["cousin", "grand_parent"]:
            raise ValidationError(_('Direct connection with "{}" relation type is not allowed, it is automatically linked'.format(self.relation_type)))

    def create_reverse_mapping(self):
        if self.RELATION_REVERSE_MAPPING.get(self.relation_type, None):
            reverse_relation = Connection.objects.get_or_create(
                people=self.related_person,
                relation_type=self.RELATION_REVERSE_MAPPING.get(self.relation_type),
                related_person=self.people,
                defaults={
                    "people_id": self.related_person.id,
                    "related_person_id": self.people.id,
                    "relation_type": self.RELATION_REVERSE_MAPPING.get(self.relation_type)
                })

    def create_parent_sibling_mapping(self):
        if self.relation_type in ['parent', 'children']:
            parent = self.people if self.relation_type == "parent" else self.related_person
            child = self.people if self.relation_type == "children" else self.related_person
            # get all children of parent 
            all_siblings = Connection.objects.filter(relation_type="children", related_person=parent).only('people_id')
            for sibling in all_siblings:
                if sibling.people_id == child.id:
                    continue

                Connection.objects.get_or_create(
                    people=child,
                    relation_type="sibling",
                    related_person_id=sibling.people_id,
                    defaults={
                        "people_id": child.id,
                        "related_person_id": sibling.people_id,
                        "relation_type": "sibling"
                    })

            # mapping the new child to other parent
            other_parent = Connection.objects.filter(relation_type="spouse", people=parent).values('related_person_id')
            if other_parent:
                Connection.objects.get_or_create(
                    people=child,
                    relation_type="children",
                    related_person_id=other_parent[0]['related_person_id'],
                    defaults={
                        "people_id": child.id,
                        "relation_type": "children",
                        "related_person_id": other_parent[0]['related_person_id']
                    })

    def save(self, *args, **kwargs):
        super(Connection, self).save(*args, **kwargs)
        # adding reverse connection (if not present)
        self.create_reverse_mapping()
        self.create_parent_sibling_mapping()

    class Meta:
        unique_together = ('people', 'related_person')    
        
    
    
