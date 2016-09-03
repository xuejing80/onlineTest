from django.contrib import admin
# Register your models here.
from work.models import HomeWork , HomeworkAnswer, BanJi, MyHomework

admin.site.register(HomeWork)
admin.site.register(HomeworkAnswer)
admin.site.register(BanJi)
admin.site.register(MyHomework)