from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.http import is_safe_url
from rest_framework import renderers


class NautobotHTMLRender(renderers.BrowsableAPIRenderer):
    template = "dcim/site_edit.html"
    default_return_url = None

    def get_return_url(self, request, view, obj=None):

        # First, see if `return_url` was specified as a query parameter or form data. Use this URL only if it's
        # considered safe.
        query_param = request.GET.get("return_url") or request.POST.get("return_url")
        if query_param and is_safe_url(url=query_param, allowed_hosts=request.get_host()):
            return query_param

        # Next, check if the object being modified (if any) has an absolute URL.
        # Note that the use of both `obj.present_in_database` and `obj.pk` is correct here because this conditional
        # handles all three of the create, update, and delete operations. When Django deletes an instance
        # from the DB, it sets the instance's PK field to None, regardless of the use of a UUID.
        if obj is not None and obj.present_in_database and obj.pk and hasattr(obj, "get_absolute_url"):
            return obj.get_absolute_url()

        # Fall back to the default URL (if specified) for the view.
        if self.default_return_url is not None:
            return reverse(self.default_return_url)

        # Attempt to dynamically resolve the list view for the object
        if hasattr(view, "queryset"):
            model_opts = view.queryset.model._meta
            try:
                prefix = "plugins:" if model_opts.app_label in settings.PLUGINS else ""
                return reverse(f"{prefix}{model_opts.app_label}:{model_opts.model_name}_list")
            except NoReverseMatch:
                pass

        # If all else fails, return home. Ideally this should never happen.
        return reverse("home")

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)

        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']

        obj = view.get_object()

        #
        # This is literally just cheating and using the existing Form object,
        # and skimming over all of the code that uses the serializer to generate
        # a form.
        #
        # from nautobot.dcim.forms import SiteForm
        # form = SiteForm(instance=obj, initial=request.data)

        #
        # This renders the form as HTML, so the `dcim/site_edit.html` template
        # needs the "form" block to just have {{ form }} as the content
        # rendering this context variable directly as HTML.
        #
        # form = self.get_rendered_html_form(data, view, 'GET', request)

        # This is trying to either generate a form class from the serializer, or
        # just render the form fields using the serializer in the tempalte
        # context. There is work to do here to demystify `{% render_field
        # serialier.foo style=style %}` e.g. What is style and how do we use it
        # to determine the widgets/templates used to render the field properly?
        # form_class = self.get_raw_data_form(data, view, 'GET', request)
        # form_class = form_class.__class__
        style = renderer_context.get("style", {})
        if 'template_pack' not in style:
            style['template_pack'] = 'rest_framework/vertical/'
        style['renderer'] = renderers.HTMLFormRenderer()

        context.update({
            "obj": obj,
            "obj_type": view.queryset.model._meta.verbose_name,
            # "form": data.serializer,
            "return_url": self.get_return_url(request, view, obj),
            "editing": obj.present_in_database,
            "serializer": data.serializer,
            "style": style,
        })
        breakpoint()

        return context

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
