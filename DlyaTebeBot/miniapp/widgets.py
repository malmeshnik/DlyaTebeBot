from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class ColorRadioSelect(forms.RadioSelect):
    """Кастомний віджет для вибору кольору з візуальним превью"""

    template_name = 'admin/widgets/color_radio_select.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'color-radio-select'})

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            # Додаємо колір до option для відображення в шаблоні
            option['color'] = value

        return option

    class Media:
        css = {
            'all': ('admin/css/color_radio_select.css',)
        }
