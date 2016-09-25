from work.models import HomeworkAnswer
from work.views import judge_homework
work =  HomeworkAnswer.objects.get(pk=321)
for j in work.solution_set.all():
    if j.result in [0,1,2,3]:
        j.result = 0
        j.save()
    else:
        continue
judge_homework(work)
print('judge done')

from work.models import MyHomework
for i in MyHomework.objects.all():
    for j in i.homeworkanswer_set.all():
        if not (j.creator in i.finished_students.all()):
            print(str(j.creator.id_num) + ' '+ str(i.id))