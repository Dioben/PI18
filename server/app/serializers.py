import datetime
import time

from rest_framework import serializers

from app.models import Simulation, Update


class SimulationSerializer(serializers.ModelSerializer):
    current_epoch = serializers.SerializerMethodField()

    class Meta:
        model = Simulation
        fields = "__all__"

    def get_current_epoch(self, obj):
        if obj.current_epoch:
            return UpdateSerializer(obj.current_epoch).data
        return None


class UpdateSerializer(serializers.ModelSerializer):
    sim = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Update
        fields = "__all__"

    def get_sim(self, obj):
        return str(obj.sim.id)

    def get_time(self, obj):
        return int(datetime.datetime.timestamp(obj.time)*1000)
