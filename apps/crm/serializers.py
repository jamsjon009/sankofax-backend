from rest_framework import serializers
from .models import Lead, LeadNote, SupportTicket


class LeadNoteSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)

    class Meta:
        model = LeadNote
        fields = ['id', 'author_email', 'body', 'created_at']
        read_only_fields = ['id', 'author_email', 'created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class LeadSerializer(serializers.ModelSerializer):
    notes = LeadNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'phone', 'source', 'status', 'assigned_to', 'notes', 'created_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SupportTicket
        fields = ['id', 'user_email', 'subject', 'message', 'status', 'priority', 'assigned_to', 'created_at', 'resolved_at']
        read_only_fields = ['id', 'user_email', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
