from django.forms.widgets import FileInput
from django.utils.html import format_html

class MultipleFileInput(FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return None