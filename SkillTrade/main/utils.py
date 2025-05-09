from django.conf import settings


class DefaultImageMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image'] = settings.MEDIA_URL + settings.DEFAULT_USER_IMAGE
        return context