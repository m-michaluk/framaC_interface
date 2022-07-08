from django.contrib import admin

# Register your models here.
from .models import File
from .models import Directory
from .models import FileSection
from .models import StatusData
from .models import SectionCategory
from .models import SectionStatus


admin.site.register(File)
admin.site.register(Directory)
admin.site.register(SectionStatus)
admin.site.register(StatusData)
admin.site.register(SectionCategory)
admin.site.register(FileSection)
