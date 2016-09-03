from django.db import models

from auth_system.models import MyUser


class BanJi(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name='班级名称')
    teacher = models.ForeignKey(MyUser, null=True, related_name='banJi_teacher')
    students = models.ManyToManyField(MyUser, related_name='banJi_students')
    courser = models.ForeignKey('judge.ClassName', null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name


class HomeWork(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    courser = models.ForeignKey('judge.ClassName', verbose_name='所属课程')
    creater = models.ForeignKey(MyUser, verbose_name='创建者')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    problem_ids = models.CharField(max_length=200, verbose_name='编程题列表id列表')
    choice_problem_ids = models.CharField(max_length=200, verbose_name='选择题id列表')
    problem_info = models.TextField()
    choice_problem_info = models.TextField()
    allowed_languages = models.CharField(max_length=50)
    total_score = models.IntegerField()

    def __str__(self):
        return self.name


class MyHomework(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    courser = models.ForeignKey('judge.ClassName', verbose_name='所属课程')
    creater = models.ForeignKey(MyUser, verbose_name='创建者')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    problem_ids = models.CharField(max_length=200, verbose_name='编程题列表id列表', null=True, blank=True)
    choice_problem_ids = models.CharField(max_length=200, verbose_name='选择题id列表', null=True, blank=True)
    problem_info = models.TextField(null=True, blank=True)
    choice_problem_info = models.TextField(null=True, blank=True)
    allowed_languages = models.CharField(max_length=50)
    banji = models.ManyToManyField(BanJi)
    finished_students = models.ManyToManyField(MyUser, related_name='finished_students', null=True, blank=True)
    total_score = models.IntegerField()

    def __str__(self):
        return self.name


class HomeworkAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    homework = models.ForeignKey(MyHomework, null=True)
    creator = models.ForeignKey(MyUser, null=True)
    wrong_choice_problems = models.CharField(max_length=200, null=True)
    wrong_choice_problems_info = models.CharField(max_length=200, null=True)
    score = models.IntegerField(null=True)
    choice_problem_score = models.IntegerField(null=True)
    problem_score = models.IntegerField(null=True)
    choice_problem_review_info = models.CharField(max_length=500)
    create_time = models.DateTimeField(auto_now_add=True)
    judged = models.BooleanField(default=False)
