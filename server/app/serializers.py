from rest_framework import serializers

from app.models import Simulation, Update


class SimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = "__all__"


class UpdateSerializer(serializers.ModelSerializer):
    sim = serializers.SerializerMethodField()

    class Meta:
        model = Update
        fields = "__all__"

    def get_sim(self, obj):
        return str(obj.sim.id)
