import uuid

from django.core.validators import MinValueValidator
from django.db import models
from timescale.db.models.models import TimescaleModel
from django.contrib.auth.models import User
# Create your models here.
#TODO: INIT DB ON DOCKER SIDE
class Simulation(TimescaleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    model = models.TextField()
    isdone = models.BooleanField()
    isrunning = models.BooleanField()
    biases = models.BinaryField()
    epoch_interval = models.IntegerField(validators=[MinValueValidator(0)])
    goal_epochs = models.IntegerField()
    #insert more stats/goals here

class Update(TimescaleModel):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    loss = models.FloatField()
    accuracy = models.FloatField()
    weights = models.BinaryField()

class Tagged(models.Model):
    tag = models.CharField(max_length=200)
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)