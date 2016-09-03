# -*- coding: utf-8 -*-
import os
import random
import shutil
import string
import zipfile
from django.apps import apps
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse
import json
from judge.forms import ProblemAddForm, ChoiceAddForm
from .models import KnowledgePoint1, ClassName, ChoiceProblem, Problem
from django.views.generic.detail import DetailView
import codecs


# 添加编程题
@permission_required('judge.add_choiceproblem')
def add_choice(request):
    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            choice_problem = form.save(user=request.user)
            return redirect(reverse("choice_problem_detail", args=[choice_problem.id]))
    else:
        form = ChoiceAddForm()
    return render(request, 'choice_problem_add.html', {'form': form})


# 添加选择题
@permission_required('judge.add_problem')
def add_problem(request):
    if request.method == 'POST':  # 当提交表单时
        form = ProblemAddForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            problem = form.save(user=request.user)  # 保存题目
            old_path = '/tmp/' + request.POST['random_name'] + '/' + request.POST['file_name'] + '_files/'
            shutil.move(old_path, '/home/judge/data/')
            os.rename('/home/judge/data/' + request.POST['file_name'] + '_files',
                      '/home/judge/data/' + str(problem.problem_id))
            print(request.POST['random_name'])
            shutil.rmtree('/tmp/' + request.POST['random_name'])
            return redirect(reverse("problem_detail", args=[problem.problem_id]))
    else:  # 当正常访问时
        form = ProblemAddForm()
    return render(request, 'problem_add.html', {'form': form})


# 删除编程题
@permission_required('judge.delete_problem')
def delete_problem(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                if os.path.exists('/home/judge/data/' + str(pk)):
                    shutil.rmtree('/home/judge/data/' + str(pk))
                Problem.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 删除选择题
@permission_required('judge.delete_choiceproblem')
def del_choice_problem(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                ChoiceProblem.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 处理选择知识点时的ajax请求
def select_point(request):
    response_data = {}
    course = request.POST.get('course', -1)
    parent = request.POST.get('parent', -1)

    if course == -1:
        point1 = KnowledgePoint1.objects.get(pk=parent)
        points = point1.knowledgepoint2_set
    else:
        course = ClassName.objects.get(pk=course)
        points = course.knowledgepoint1_set
    for point in points.all():
        response_data[point.id] = point.name
    return HttpResponse(json.dumps(response_data), content_type='application/json')


#  编程题详细视图
class ProblemDetailView(DetailView):
    model = Problem
    template_name = 'problem_detail.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView, self).get_context_data(**kwargs)
        str = ''
        for point in self.object.knowledgePoint2.all():
            str += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '\n'
        context['knowledge_point'] = str
        return context


# 选择题详细视图
class ChoiceProblemDetailView(DetailView):
    model = ChoiceProblem
    template_name = 'choice_problem_detail.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super(ChoiceProblemDetailView, self).get_context_data(**kwargs)
        str = ''
        for point in self.object.knowledgePoint2.all():
            str += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '\n'
        context['knowledge_point'] = str
        return context


# 更新编程题
@permission_required('judge.change_problem')
def update_problem(request, id):
    problem = get_object_or_404(Problem, pk=id)
    json_dic = {}  # 知识点选择的需要的初始化数据
    for point in problem.knowledgePoint2.all():
        json_dic[point.id] = point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name
    initial = {'title': problem.title,
               'description': problem.description,
               'time_limit': problem.time_limit,
               'memory_limit': problem.memory_limit,
               'input': problem.input,
               'output': problem.output,
               'sample_input': problem.sample_input,
               'sample_output': problem.sample_output,
               'sample_input2': problem.sample_input2,
               'sample_output2': problem.sample_output2,
               'classname': 0,
               'keypoint': json.dumps(json_dic, ensure_ascii=False).encode('utf8')
               }  # 生成表单的初始化数据
    if request.method == "POST":  # 当提交表单时
        form = ProblemAddForm(request.POST)
        if form.is_valid():
            form.save(user=request.user, problemid=id)
            try:  # 对文件进行解压和保存
                f = request.FILES['file_upload']
                store_dir = '/home/judge/data/' + str(problem.problem_id)
                if os.path.exists(store_dir):
                    shutil.rmtree(store_dir)
                os.makedirs(store_dir)
                with open(store_dir + '/file.zip', 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chdir(store_dir)
                shutil.unpack_archive('file.zip')
                os.remove('file.zip')
            except Exception as  e:
                print(e)
                pass
            return redirect(reverse("problem_detail", args=[id]))
    return render(request, 'problem_add.html', {'form': ProblemAddForm(initial=initial)})


@permission_required('judge.change_choiceproblem')
def update_choice_problem(request, id):
    problem = get_object_or_404(ChoiceProblem, pk=id)
    json_dic = {}  # 知识点选择的需要的初始化数据
    for point in problem.knowledgePoint2.all():
        json_dic[point.id] = point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name
    initial = {'title': problem.title,
               'a': problem.a,
               'b': problem.b,
               'c': problem.c,
               'd': problem.d,
               'selection': problem.right_answer,
               'classname': 0,
               'keypoint': json.dumps(json_dic, ensure_ascii=False).encode('utf8')
               }  # 生成表单的初始化数据
    if request.method == "POST":  # 当提交表单时
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            form.save(user=request.user, id=id)
            return redirect(reverse("choice_problem_detail", args=[id]))
    return render(request, 'choice_problem_add.html', {'form': ChoiceAddForm(initial=initial)})


# 编程提列表
@permission_required('judge.add_problem')
def list_problems(request):
    classnames = ClassName.objects.all()
    return render(request, 'problem_list.html', context={'classnames': classnames})


# 选择题列表
@permission_required('judge.add_choiceproblem')
def list_choices(request):
    classnames = ClassName.objects.all()
    return render(request, 'choice_problem_list.html', context={'classnames': classnames})


# 返回含有问题数据的json
def get_json(request, model_name):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    knowledgePoint2 = request.GET['knowledgePoint2']
    classname = request.GET['classname']
    knowledgePoint1 = request.GET['knowledgePoint1']
    model = apps.get_model(app_label='judge', model_name=model_name)
    if knowledgePoint2 != '0':
        problems = model.objects.filter(knowledgePoint2__id=knowledgePoint2)
    elif knowledgePoint1 != '0':
        problems = model.objects.filter(knowledgePoint1__id=knowledgePoint1)
    elif classname != '0':
        problems = model.objects.filter(classname__id=classname)
    else:
        problems = model.objects
    try:
        problems = problems.filter(title__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = problems.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for problem in problems.all().order_by(sort)[offset:offset + limit]:
        knowledge_point = ''
        if isinstance(problem, Problem):
            testCases = get_testCases(problem)
            total_score = get_totalScore(testCases)
        else:
            testCases = 0
            total_score = 5
        for point in problem.knowledgePoint2.all():
            knowledge_point += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '<br>'
        recode = {'title': problem.title, 'pk': problem.pk,
                  'update_date': problem.update_date.strftime('%Y-%m-%d %H:%M:%S'), 'id': problem.pk,
                  'knowledge_point': knowledge_point, 'testcases': testCases, 'total_score': total_score}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


# 获取指定题目的分值信息
def get_testCases(problem):
    cases = []
    filename = '/home/judge/data/' + str(problem.problem_id) + "/scores.txt"
    data = open(filename).read()
    if data[:3] == codecs.BOM_UTF8:  # 去除bom
        data = data[3:]
    lines = data.splitlines()
    for line in lines:
        if line:
            desc, score = line.split()[:2]
            case = {'desc': desc, 'score': int(score)}
            cases.append(case)
    return cases


def get_totalScore(test_cases):
    total_score = 0
    for score in test_cases:
        total_score += score['score']
    return total_score


@permission_required('judge.add_problem')
def verify_file(request):
    file = request.FILES['file_upload']
    count = 0
    in_count = 0
    out_count = 0
    random_name = ''.join(random.sample(string.digits + string.ascii_letters * 10, 8))
    tempdir = os.path.join('/tmp', random_name)
    os.mkdir(tempdir)
    filename = os.path.join(tempdir, file.name)
    with open(filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    un_zip(filename)
    try:
        score_filename = filename + '_files/' "scores.txt"
        data = open(score_filename).read()
        if data[:3] == codecs.BOM_UTF8:  # 去除bom
            data = data[3:]
        lines = data.splitlines()
        for line in lines:
            if line:
                desc, score = line.split()[:2]
            count += 1
    except:
        shutil.rmtree(tempdir)
        return HttpResponse(json.dumps({'result': 0, 'info': 'scores.txt文件不符合规范，请注意文件最后不要多余空行'}))
    for parentdir, dirname, filenames in os.walk(filename + '_files/'):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.in':
                in_count += 1
            elif os.path.splitext(filename)[1] == '.out':
                out_count += 1
    if in_count != count:
        shutil.rmtree(tempdir)
        return HttpResponse(json.dumps({'result': 0, 'info': '.in文件数量与scores.txt中的评分项目不符'}))
    if out_count != count:
        shutil.rmtree(tempdir)
        return HttpResponse(json.dumps({'result': 0, 'info': '.out文件数量与scores.txt中的评分项目不符'}))
    return HttpResponse(json.dumps({"result": 1, 'info': random_name, 'filename': file.name}))


def un_zip(file_name):
    zip_file = zipfile.ZipFile(file_name)
    os.mkdir(file_name + "_files")
    for names in zip_file.namelist():
        zip_file.extract(names, file_name + "_files/")
    zip_file.close()
