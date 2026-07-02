from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework import serializers as drf_serializers
from .models import Subscriber


class SubscribeSerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField()
    source = drf_serializers.ChoiceField(choices=Subscriber.Source.choices, default='homepage')


class SubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub, created = Subscriber.objects.get_or_create(
            email=serializer.validated_data['email'],
            defaults={'source': serializer.validated_data.get('source', 'homepage')},
        )
        if not created and not sub.is_active:
            sub.is_active = True
            sub.save(update_fields=['is_active'])
        return Response({'subscribed': True}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
