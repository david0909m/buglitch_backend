from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):

    created_by = serializers.ReadOnlyField(
        source='created_by.username'
    )

    workspace_name = serializers.CharField(
        source='workspace.name',
        read_only=True
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'created_by',
            'created_at',
            'updated_at',
        ]
