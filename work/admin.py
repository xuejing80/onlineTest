from django.contrib import admin
# Register your models here.
from work.models import HomeWork , HomeworkAnswer, BanJi, MyHomework, TempHomeworkAnswer

admin.site.register(HomeWork)
admin.site.register(HomeworkAnswer)
admin.site.register(BanJi)
admin.site.register(MyHomework)
admin.site.register(TempHomeworkAnswer)