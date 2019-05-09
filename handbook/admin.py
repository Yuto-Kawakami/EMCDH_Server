from django.contrib import admin
from .models import User, Health, Pregnancy, ConsultationRecord, Child, GPAC

# Register your models here.
admin.site.register(User)
admin.site.register(GPAC)
admin.site.register(Health)
admin.site.register(Pregnancy)
admin.site.register(ConsultationRecord)
admin.site.register(Child)