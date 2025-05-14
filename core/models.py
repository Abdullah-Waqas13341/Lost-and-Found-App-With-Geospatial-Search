from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.gis.geos import Point
from .utils import geocode_location, get_solr_core
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests

# Solr core mapping


class User(AbstractUser):
    nust_id = models.IntegerField(unique=True, verbose_name="NUST ID")
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)

    REQUIRED_FIELDS = ['nust_id', 'email']

    def __str__(self):
        return f'{self.full_name} ({self.username})' if self.full_name else self.username

class LostItem(models.Model):
    STATUS_CHOICES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found'),
        ('RESOLVED', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    location_text = models.CharField(max_length=200)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    image = models.ImageField(upload_to='lost_items/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)  # <-- Add this line

    def save(self, *args, **kwargs):
        if self.location_text and not self.location:
            coords = geocode_location(self.location_text)
            if coords:
                self.location = Point(coords[0], coords[1])
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.status}'

@receiver(post_save, sender=LostItem)
def index_lostitem_to_solr(sender, instance, **kwargs):
    core = get_solr_core(instance.location_text)
    if not core:
        return
    solr_url = f'http://localhost:8983/solr/{core}/update/json/docs?commit=true'
    doc = {
        'id': instance.id,
        'title': instance.title,
        'description': instance.description,
        'category': instance.category,
        'location': instance.location_text,
        'status': instance.status,
        'reported_at': instance.reported_at.isoformat(),
    }
    try:
        requests.post(solr_url, json=[doc])
    except Exception as e:
        # Optionally log the error
        pass