from django import forms
from django.db import models

from .models import File
from .models import Directory


class UploadFileModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        _user =  kwargs.pop("owner")
        super(UploadFileModelForm, self).__init__(*args, **kwargs)
        self.fields['parent'] = forms.ModelChoiceField(queryset=Directory.objects.filter(owner=_user).exclude(availabilityFlag=False), empty_label=None, label="Folder")

    class Meta:
        model = File
        fields = ['name', 'description', 'file_field', 'parent']
        labels = {
            "file_field": "",
        }



class AddDirectoryModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user =  kwargs.pop("owner")
        super(AddDirectoryModelForm, self).__init__(*args, **kwargs)
        self.fields['parent'] = forms.ModelChoiceField(queryset=Directory.objects.filter(owner=user).exclude(availabilityFlag=False), empty_label=None, label="Folder")

    class Meta:
        model = Directory
        fields = ['name', 'description', 'parent']



class VCForm(forms.Form):
    VC_CHOICES = (
    ('-wp-rte', '-wp-rte'),    
    ('-wp-prop="@lemma"', '-wp-prop="@lemma"'),
    ('-wp-prop="@requires"', '-wp-prop="@requires"'),
    ('-wp-prop="@assigns"', '-wp-prop="@assigns"'),
    ('-wp-prop="@ensures"', '-wp-prop="@ensures"'),
    ('-wp-prop="@exits"', '-wp-prop="@exits"'),
    ('-wp-prop="@assert"', '-wp-prop="@assert"'),
    ('-wp-prop="@complete_behaviors"', '-wp-prop="@complete_behaviors"'),
    ('-wp-prop="@disjoint_behaviors"', '-wp-prop="@disjoint_behaviors"'),
    ('-wp-prop="@-lemma"', '-wp-prop="@-lemma"'),
    ('-wp-prop="@-requires"', '-wp-prop="@-requires"'),
    ('-wp-prop="@-assigns"', '-wp-prop="@-assigns"'),
    ('-wp-prop="@-ensures"', '-wp-prop="@-ensures"'),
    ('-wp-prop="@-exits"', '-wp-prop="@-exits"'),
    ('-wp-prop="@-assert"', '-wp-prop="@-assert"'),
    ('-wp-prop="@-complete_behaviors"', '-wp-prop="@-complete_behaviors"'),
    ('-wp-prop="@-disjoint_behaviors"', '-wp-prop="@-disjoint_behaviors"'),
    )
    vcs = forms.MultipleChoiceField(choices=VC_CHOICES, widget=forms.CheckboxSelectMultiple(
                                        attrs={
                                            'class':'choices',
                                            }
                                        ),
                                        label="Choose VCs",
                                        required=False,                    
                                    )

