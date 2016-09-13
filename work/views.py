# encoding: utf-8
import json
import time
import _thread
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from auth_system.models import MyUser
from judge.models import ClassName, Problem, ChoiceProblem, Solution, SourceCode, SourceCodeUser, KnowledgePoint1, \
    KnowledgePoint2
from work.models import HomeWork, HomeworkAnswer, BanJi, MyHomework
from django.contrib.auth.decorators import permission_required, login_required


@permission_required('work.add_homework')
def add_homework(request):
    if request.method == 'POST':
        print(','.join(request.POST.getlist('languages')))
        homework = HomeWork(name=request.POST['name'],
                            choice_problem_ids=request.POST['choice-problem-ids'],
                            problem_ids=request.POST['problem-ids'],
                            problem_info=request.POST['problem-info'],
                            choice_problem_info=request.POST['choice-problem-info'],
                            courser=ClassName.objects.get(pk=request.POST['classname']),
                            start_time=request.POST['start_time'],
                            end_time=request.POST['end_time'],
                            allowed_languages=','.join(request.POST.getlist('languages')),
                            total_score=request.POST['total_score'],
                            creater=request.user)
        homework.save()
        return redirect(reverse("homework_detail", args=[homework.pk]))
    classnames = ClassName.objects.all()
    return render(request, 'homework_add.html', context={'classnames': classnames, 'title': '新建作业'})


# 获取作业列表数据
@permission_required('work.change_homework')
def get_json_work(request):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    if request.GET['my'] == 'true':
        homeworks = MyHomework.objects.filter(creater=request.user).all()
    else:
        homeworks = HomeWork.objects.all()
    if classname != '0':
        homeworks = homeworks.filter(courser__id=classname)
    try:
        homeworks = homeworks.filter(name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = homeworks.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework in homeworks.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': homework.name, 'pk': homework.pk,
                  'courser': homework.courser.name, 'id': homework.pk,
                  'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S')}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


@permission_required('work.add_homework')
def list_homework(request):
    context = {'classnames': ClassName.objects.all()}
    return render(request, 'homework_list.html', context=context)


# 删除作业
@permission_required('work.delete_homework')
def del_homework(request):
    if request.method == 'POST':
        my = request.POST['my']
        ids = request.POST.getlist('ids[]')
        if my == 'true':
            objects = MyHomework.objects
        else:
            objects = HomeWork.objects
        try:
            for pk in ids:
                objects.get(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 显示作业详细
@permission_required('work.change_homework')
def show_homework(request, pk):
    homework = get_object_or_404(HomeWork, pk=pk)
    context = {'id': homework.id, 'name': homework.name, 'courser': homework.courser.name,
               'start_time': homework.start_time, 'end_time': homework.end_time,
               'title': '公开作业“' + homework.name + '”的详细'}
    return render(request, 'homework_detail.html', context=context)


# 显示我的作业详细
@permission_required('work.change_homework')
def show_my_homework(request, pk):
    homework = get_object_or_404(MyHomework, pk=pk)
    total_students_number = 0
    for banji in homework.banji.all():
        total_students_number += banji.students.count()
    context = {'id': homework.id, 'name': homework.name, 'courser': homework.courser.name,
               'start_time': homework.start_time, 'end_time': homework.end_time, 'banjis': homework.banji.all(),
               "finished_students_number": homework.finished_students.count(),
               'total_students_number': total_students_number, 'title': '我的私有作业“' + homework.name + '”的详细'}
    return render(request, 'my_homework_detail.html', context=context)


# 处理作业详细请求
@permission_required('work.change_homework')
def ajax_for_homework_info(request):
    homework_id = request.POST['homework_id']
    if request.POST['my'] == 'true':
        homework = MyHomework.objects.get(pk=homework_id)
    else:
        homework = HomeWork.objects.get(pk=homework_id)
    result = {'problem_info': json.loads(homework.problem_info),
              'choice_problem_info': json.loads(homework.choice_problem_info)}
    return HttpResponse(json.dumps(result))


@permission_required('work.change_homework')
def update_public_homework(request, pk):
    homework = get_object_or_404(HomeWork, pk=pk)
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.courser = ClassName.objects.get(pk=request.POST['classname'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.problem_info = request.POST['problem-info']
        homework.total_score = request.POST['total_score']
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.save()
        return redirect(reverse("homework_detail", args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id, 'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改公开作业 "' + homework.name + '"'}
    return render(request, 'homework_add.html', context=context)


@permission_required('work.change_homework')
def update_my_homework(request, pk):
    homework = get_object_or_404(MyHomework, pk=pk)
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.courser = ClassName.objects.get(pk=request.POST['classname'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.problem_info = request.POST['problem-info']
        homework.total_score = request.POST['total_score']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.save()
        return redirect(reverse('my_homework_detail', args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id, 'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改我的作业"' + homework.name + '"'}
    return render(request, 'homework_add.html', context=context)  # 查看作业结果


@login_required()
def show_homework_result(request, id):
    homework_answer = HomeworkAnswer.objects.get(pk=id)
    if request.user != homework_answer.creator:
        return render(request, 'warning.html', context={
            'info': '您无权查看其他同学的作业结果'})
    if not homework_answer.judged:
        return render(request, 'information.html', context={
            'info': '作业正在批改,请稍后刷新查看或到已完成作业列表中查看'})
    wrong_id = homework_answer.wrong_choice_problems.split(',')
    wrong_info = homework_answer.wrong_choice_problems_info.split(',')
    homework = homework_answer.homework
    choice_problems = []
    for info in json.loads(homework.choice_problem_info):
        if str(info['id']) in wrong_id:
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': False,
                 'info': wrong_info[wrong_id.index(str(info['id']))]})
        else:
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': True}
            )
    return render(request, 'homework_result.html',
                  context={'choice_problems': choice_problems, 'problem_score': homework_answer.problem_score,
                           'choice_problem_score': homework_answer.choice_problem_score,
                           'score': homework_answer.score})


def get_choice_score(homework_answer):
    choice_problem_score = 0
    for info in json.loads(homework_answer.homework.choice_problem_info):
        if str(info['id']) not in homework_answer.wrong_choice_problems.split(','):
            choice_problem_score += int(info['total_score'])
    return choice_problem_score


# 显示作业并处理作业答案
@login_required()
def do_homework(request, homework_id):
    if request.method == 'POST':
        wrong_ids, wrong_info = '', ''
        homeworkAnswer = HomeworkAnswer()
        homeworkAnswer.save()
        homework = MyHomework.objects.get(pk=homework_id)
        if request.user in homework.finished_students.all():
            return render(request, 'warning.html', context={'info': '您已提交过此题目，请勿重复提交'})
        for id in homework.choice_problem_ids.split(','):
            if id and request.POST.get('selection-' + id, 'x') != ChoiceProblem.objects.get(pk=id).right_answer:
                wrong_ids += id + ','
                wrong_info += request.POST.get('selection-' + id, '未回答') + ','
        for k, v in request.POST.items():
            if k.startswith('source'):
                solution = Solution(problem_id=k[7:], user_id=request.user.username,
                                    language=request.POST['language-' + k[7:]], ip=request.META['REMOTE_ADDR'],
                                    code_length=len(v))
                solution.save()
                homeworkAnswer.solution_set.add(solution)
                source_code = SourceCode(solution_id=solution.solution_id, source=v)
                source_code.save()
                source_code_user = SourceCodeUser(solution_id=solution.solution_id, source=v)
                source_code_user.save()
        homeworkAnswer.wrong_choice_problems = wrong_ids
        homeworkAnswer.wrong_choice_problems_info = wrong_info
        homeworkAnswer.creator = request.user
        homeworkAnswer.homework = homework
        homeworkAnswer.save()
        homework.finished_students.add(request.user)
        _thread.start_new_thread(judge_homework, (homeworkAnswer,))
        return redirect(reverse('show_homework_result', args=[homeworkAnswer.id]))
    else:
        homeowork = MyHomework.objects.get(pk=homework_id)
        choice_problems = []
        for id in homeowork.choice_problem_ids.split(','):
            if id:
                choice_problems.append({'detail': ChoiceProblem.objects.get(pk=id),
                                        'score': json.loads(homeowork.choice_problem_info)[0]['total_score']})
        problems = []
        for id in homeowork.problem_ids.split(','):
            if id:
                problems.append(Problem.objects.get(pk=id))
        return render(request, 'do_homework.html',
                      context={'homework': homeowork, 'problems': problems, 'choice_problems': choice_problems})


# 新建班级

@permission_required('work.add_banji')
def add_banji(request):
    if request.method == 'POST':
        banji = BanJi(name=request.POST['name'], start_time=request.POST['start_time'], teacher=request.user,
                      end_time=request.POST['end_time'],
                      courser=ClassName.objects.get(pk=request.POST['classname']))
        banji.save()
        return redirect(reverse('banji_detail', args=(banji.id,)))
    return render(request, 'banji_add.html', context={'classnames': ClassName.objects.all(), 'title': "新建班级"})


@permission_required('work.add_classname')
def add_courser(request):
    courser = ClassName(name=request.POST['name'])
    courser.save()
    return HttpResponse(1)


# 显示班级列表
@permission_required('work.add_banji')
def list_banji(request):
    classnames = ClassName.objects.all()
    context = {'classnames': classnames, 'title': '班级列表'}
    return render(request, 'banji_list.html', context=context)


# 获取班级列表信息
@permission_required('work.add_banji')
def get_banji_list(request):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    if request.GET['my'] == 'true':
        objects = BanJi.objects.filter(teacher=request.user)
    else:
        objects = BanJi.objects
    if classname != '0':
        banjis = objects.filter(courser__id=classname)
    else:
        banjis = objects
    try:
        banjis = banjis.filter(name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = banjis.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for banji in banjis.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': banji.name, 'pk': banji.pk,
                  'courser': banji.courser.name, 'id': banji.pk, 'teacher': banji.teacher.username,
                  'start_time': banji.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'end_time': banji.end_time.strftime('%Y-%m-%d %H:%M:%S')}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


# 删除班级
@permission_required('work.delete_banji')
def del_banji(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                BanJi.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 更新班级信息
@permission_required('work.change_banji')
def update_banji(request, id):
    banji = get_object_or_404(BanJi, pk=id)
    if request.method == 'POST':
        banji.name = request.POST['name']
        banji.start_time = request.POST['start_time']
        banji.end_time = request.POST['end_time']
        banji.courser = ClassName.objects.get(pk=request.POST['classname'])
        banji.save()
        return redirect(reverse('banji_detail', args=(banji.id,)))
    else:
        return render(request, 'banji_add.html',
                      context={'name': banji.name, 'start_time': banji.start_time, 'end_time': banji.end_time,
                               'courser_id': banji.courser.pk, 'classnames': ClassName.objects.all(),
                               'title': '修改班级信息'})


# 复制公共作业到私有作业
@permission_required('work.add_myhomework')
def copy_to_my_homework(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                old_homework = HomeWork.objects.get(pk=pk)
                homework = MyHomework(name=old_homework.name, courser=old_homework.courser, creater=request.user,
                                      start_time=old_homework.start_time, end_time=old_homework.end_time,
                                      problem_ids=old_homework.problem_ids,
                                      choice_problem_ids=old_homework.choice_problem_ids,
                                      problem_info=old_homework.problem_info,
                                      choice_problem_info=old_homework.choice_problem_info,
                                      allowed_languages=old_homework.allowed_languages,
                                      total_score=old_homework.total_score)
                homework.save()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


@permission_required('work.add_homework')
def list_my_homework(request):
    classnames = ClassName.objects.all()
    context = {'classnames': classnames, 'title': '我的私有作业列表'}
    return render(request, 'my_homework_list.html', context=context)


@permission_required('work.add_banji')
def show_banji(request, pk):
    banji = BanJi.objects.get(pk=pk)
    context = {'id': banji.id, 'name': banji.name, 'courser': banji.courser.name, 'start_time': banji.start_time,
               'end_time': banji.end_time, 'teacher': banji.teacher.username, 'students': banji.students.all(),
               'title': '班级"' + banji.name + '"的信息'}
    return render(request, 'banji_detail.html', context=context)


@permission_required('work.change_banji')
def add_students(request, pk):
    return render(request, 'add_students.html', context={'id': pk, 'title': '添加学生到班级'})


@permission_required('work.change_banji')
def ajax_add_students(request):
    stu_detail = request.POST['stu_detail']
    banji_id = request.POST['banji_id']
    if len(stu_detail.split()) > 1:
        id_num, username = stu_detail.split()[0], stu_detail.split()[1]
        try:
            student = MyUser.objects.get(id_num=id_num)
        except:
            student = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
            student.set_password(id_num)
            student.save()
            student.groups.add(Group.objects.get(name='学生'))
    else:
        try:
            student = MyUser.objects.get(id_num=stu_detail)
        except:
            return HttpResponse(json.dumps({'result': 0, 'message': '该学号未注册，且您未提供注册信息'}))
    banji = BanJi.objects.get(pk=banji_id)
    banji.students.add(student)
    return HttpResponse(json.dumps({'result': 0, 'count': 1}))


@permission_required('work.add_homework')
def assign_homework(request):
    homework_id = request.POST['homework_id']
    banji_id = request.POST['id']
    try:
        homework = MyHomework.objects.get(pk=homework_id)
        banji = BanJi.objects.get(pk=banji_id)
        banji.myhomework_set.add(homework)
        return HttpResponse(json.dumps({'result': 0, 'count': 1}))
    except:
        return HttpResponse(json.dumps({'result': 0, 'message': '出错了'}))


# 显示我的待做作业
@login_required()
def list_do_homework(request):
    return render(request, 'do_homework_list.html', context={'classnames': ClassName.objects.all(), 'title': '尚未完成的作业'})


# 获取待做作业列表
@login_required()
def get_my_homework_todo(request):
    user = request.user
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    homeworks = MyHomework.objects.filter(banji__students=user)
    if classname != '0':
        homeworks = homeworks.filter(courser__id=classname)
    try:
        homeworks = homeworks.filter(name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    count = 0

    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework in homeworks.all().order_by(sort)[offset:offset + limit]:

        if request.user not in homework.finished_students.all() and time.mktime(
                homework.start_time.timetuple()) < time.time() < time.mktime(homework.end_time.timetuple()):
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S')}
            recodes.append(recode)
            count += 1
    json_data['rows'] = recodes
    json_data['total'] = count
    return HttpResponse(json.dumps(json_data))


# 获取作业的编程题分数

def get_problem_score(homework_answer):
    score = 0
    homework = homework_answer.homework
    solutions = homework_answer.solution_set
    for info in json.loads(homework.problem_info):
        solution = solutions.get(problem_id=info['id'])
        for case in info['testcases']:
            if solution.oi_info == '{(null)}':
                break
            if json.loads(solution.oi_info)[case['desc'] + '.in']['result'] == 4:
                score += int(case['score'])
    return score


@login_required()
def list_finished_homework(request):
    return render(request, 'finidshed_homework_list.html',
                  context={'classnames': ClassName.objects.all(), 'title': '已经完成的作业'})


@login_required()
def get_finished_homework(request):
    json_data = {}
    recodes = []
    user = request.user
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    homework_answers = HomeworkAnswer.objects.filter(creator=user)
    if request.GET['classname'] != '0':
        homework_answers = homework_answers.filter(homework__courser=HomeWork.objects.get(pk=request.GET['classname']))
    try:
        homework_answers = homework_answers.filter(homework__name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    homework_answers = homework_answers.filter(judged=True)
    json_data['total'] = homework_answers.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework_answer in homework_answers.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': homework_answer.homework.name,
                  'create_time': homework_answer.create_time.strftime('%Y-%m-%d %H:%M:%S'), 'id': homework_answer.pk,
                  'teacher': 'dd',
                  'score': '%d/%d' % (homework_answer.score, homework_answer.homework.total_score)
                  }
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


@permission_required('work.add_homework')
def get_finished_students(request):
    json_data = {}
    recodes = []
    homework_id = request.GET['homework_id']
    homework = MyHomework.objects.get(pk=homework_id)
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    homework_answers = homework.homeworkanswer_set
    if request.GET['banji_id'] != '0':
        homework_answers = homework_answers.filter(homework__courser_id=request.GET['banji_id'])
    try:
        homework_answers = homework_answers.filter(homework__name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    homework_answers = homework_answers.filter(judged=True)
    json_data['total'] = homework_answers.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework_answer in homework_answers.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': homework_answer.creator.username,
                  'create_time': homework_answer.create_time.strftime('%Y-%m-%d %H:%M:%S'), 'id': homework_answer.id,
                  'teacher': 'dd',
                  'score': '%d/%d' % (homework_answer.score, homework_answer.homework.total_score)
                  }
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


@permission_required('work.add_classname')
def list_coursers(request):
    coursers = ClassName.objects.all()
    return render(request, 'courser_list.html', {'coursers': coursers, 'title': '课程列表'})


@permission_required('work.add_knowledgepoint1')
def list_kp1s(request, id):
    courser = ClassName.objects.get(id=id)
    kp1s = KnowledgePoint1.objects.filter(classname=courser)
    return render(request, 'kp1_list.html', {'kp1s': kp1s, 'title': '查看课程“%s”的一级知识点' % courser.name, 'id': id})


@permission_required('work.add_knowledgepoint2')
def list_kp2s(request, id):
    kp1 = KnowledgePoint1.objects.get(id=id)
    kp2s = KnowledgePoint2.objects.filter(upperPoint=kp1)
    return render(request, 'kp2s_list.html', context={'kp2s': kp2s, 'id': id, 'title': '查看一级知识点"%s”下的二级知识点' % kp1.name})


@permission_required('work.delete_classname')
def delete_courser(request):
    try:
        ClassName.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.delete_knowledgepoint1')
def delete_kp1(request):
    try:
        KnowledgePoint1.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.delete_knowledgepoint2')
def delete_kp2(request):
    try:
        KnowledgePoint2.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.add_knowledgepoint1')
def add_kp1(request):
    kp1 = KnowledgePoint1(name=request.POST['name'], classname_id=request.POST['id'])
    kp1.save()
    return HttpResponse(1)


@permission_required('work.add_knowledgepoint2')
def add_kp2(request):
    kp2 = KnowledgePoint2(name=request.POST['name'], upperPoint_id=request.POST['id'])
    kp2.save()
    return HttpResponse(1)


# 判断作业成绩并保存
def judge_homework(homework_answer):
    while True:
        for solution in homework_answer.solution_set.all():
            if not solution.oi_info:
                time.sleep(1)
                break
        else:
            choice_problem_score = get_choice_score(homework_answer)
            homework_answer.choice_problem_score = choice_problem_score
            problem_score = get_problem_score(homework_answer)
            homework_answer.problem_score = problem_score
            homework_answer.score = choice_problem_score + problem_score
            homework_answer.judged = True
            homework_answer.save()
            break


@permission_required('work.add_myhomework')
def add_myhomework(request):
    if request.method == 'POST':
        print(','.join(request.POST.getlist('languages')))
        homework = MyHomework(name=request.POST['name'],
                              choice_problem_ids=request.POST['choice-problem-ids'],
                              problem_ids=request.POST['problem-ids'],
                              problem_info=request.POST['problem-info'],
                              choice_problem_info=request.POST['choice-problem-info'],
                              courser=ClassName.objects.get(pk=request.POST['classname']),
                              start_time=request.POST['start_time'],
                              end_time=request.POST['end_time'],
                              allowed_languages=','.join(request.POST.getlist('languages')),
                              total_score=request.POST['total_score'],
                              creater=request.user)
        homework.save()
        return redirect(reverse("my_homework_detail", args=[homework.pk]))
    classnames = ClassName.objects.all()
    return render(request, 'homework_add.html', context={'classnames': classnames, 'title': '新建私有作业'})
