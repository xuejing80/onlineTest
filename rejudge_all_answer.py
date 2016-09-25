from work.models import MyHomework,HomeworkAnswer
from work.views import judge_homework
import _thread

for i in HomeworkAnswer.objects.all():
    if i.score and i.score != i.homework.total_score:
        for j in i.solution_set.all():
            if j.result in [0,1,2,3]:
                j.result = 0
                j.save()
        judge_homework(i)
        print('judged ' + str(i.id) )
