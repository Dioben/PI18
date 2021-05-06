import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from timescale.db.models.models import TimescaleModel
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Simulation(TimescaleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    model = models.TextField()
    isdone = models.BooleanField()
    isrunning = models.BooleanField()
    biases = models.BinaryField()
    layers = models.IntegerField()
    epoch_interval = models.IntegerField(validators=[MinValueValidator(1)])
    goal_epochs = models.IntegerField()
    #insert more stats/goals here
    class Meta:
        db_table = "Simulations"
        indexes = [models.Index(fields=["owner"])]


class Update(TimescaleModel):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    epoch = models.IntegerField()
    loss = models.FloatField()
    accuracy = models.FloatField()
    class Meta:
        db_table = "Epoch_values"
        indexes = [models.Index(fields=["sim","epoch"])]

class Weights(TimescaleModel):
    epoch = models.IntegerField()
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    layer_index = models.IntegerField() #maybe a string, i dont know what i'm doing
    weight = ArrayField(models.IntegerField())
    class Meta:
        db_table = "Weights"
        indexes =[ models.Index(fields=['sim','epoch']),models.Index(fields=['sim','layer_index'])]

class Tagged(models.Model):
    tag = models.CharField(max_length=200)
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    tagger = models.ForeignKey(User,on_delete=models.CASCADE)
    class Meta:
        unique_together = (('tag','sim'),)
        db_table = "Tags"
        indexes = [models.Index(fields=['tag']),models.Index(fields=['tagger']),models.Index(fields=["sim"])]