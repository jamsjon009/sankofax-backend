from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers as drf_serializers
from .models import SiteSetting, Page, FAQ


class ContactSerializer(drf_serializers.Serializer):
    name = drf_serializers.CharField()
    email = drf_serializers.EmailField()
    message = drf_serializers.CharField()


class SiteSettingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = SiteSetting.get()
        return Response({
            'site_name': settings.site_name,
            'contact_email': settings.contact_email,
            'footer_text': settings.footer_text,
            'social_links': settings.social_links,
            'meta_description': settings.meta_description,
        })


class PageDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            page = Page.objects.get(slug=slug, is_active=True)
            return Response({'title': page.title, 'content': page.content})
        except Page.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound()


class FAQListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        return Response([{'question': f.question, 'answer': f.answer} for f in faqs])


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.core.mail import send_mail
        from django.conf import settings
        site = SiteSetting.get()
        send_mail(
            subject=f'Contact from {serializer.validated_data["name"]}',
            message=serializer.validated_data['message'],
            from_email=serializer.validated_data['email'],
            recipient_list=[site.contact_email or settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
        # Save as CRM lead
        from apps.crm.models import Lead
        Lead.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            source=Lead.Source.CONTACT_FORM,
        )
        return Response({'sent': True})
