from django.contrib import admin

# Register your models here.
from judge.models import Problem,Solution,SourceCode,SourceCodeUser,KnowledgePoint1,KnowledgePoint2,ClassName,ChoiceProblem,Compileinfo
admin.site.register(Problem)
admin.site.register(Solution)
admin.site.register(SourceCodeUser)
admin.site.register(SourceCode)
admin.site.register(ClassName)
admin.site.register(KnowledgePoint2)
admin.site.register(KnowledgePoint1)
admin.site.register(ChoiceProblem)


class ProblemAdmin(admin.ModelAdmin):
    # list_display = ('title','description','input','output','sample_input','sample_output','spj','hint','source')
    pass