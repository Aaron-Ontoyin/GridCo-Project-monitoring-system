from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from django.db.models import Q

from .models import Project, Entry, SubPDO


class IndexView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'baseApp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('searched_project')
        projects = Project.objects.filter(
            Q(only_viewers__in=[self.request.user]) |
            Q(reporters__in=[self.request.user]) |
            Q(creator=self.request.user)
        )

        if q is not None:
            projects = projects.filter(
                Q(name__icontains=q) |
                Q(duration__icontains=q) |
                Q(creator__username__icontains=q) |
                Q(genPDO__icontains=q)
            )            
            if len(projects) == 0:
                messages.info(self.request, "Project not found. Search projects by name, creater's name or PDO")

        context['projects'] = projects[:10]
        return context


class LoginView(View):
    template_name='baseApp/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)

        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, request.POST)        
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {request.user.username}")
                return redirect(self.success_url)
            else:
                messages.error(request, "Incorrect Username or password")
        else:
            print(form.errors)
            
        return render(request, self.template_name, {'form': form, 'messages': messages})


def logoutView(request):
    logout(request)
    return redirect('login')


class ProjectView(LoginRequiredMixin, DetailView):
    model = Project
    context_object_name = 'project'
    template_name = 'baseApp/project.html'

    def get(self, request, *args, **kwargs):
        project = self.get_object()        
        self.object = project
        user = request.user
        allowed_viewers = project.reporters.all() | project.only_viewers.all()
        if project.creator == user or user in allowed_viewers:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        else:
            raise Http404("You are not authorized to view this project.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['year_entries'] = project.get_year_entries()
        context['entries_in_a_year'] = project.collection_freq.num_entries
        context['project_years'] = project.project_years.all()
        context['editable'] = True if self.request.user in project.reporters.all() else False
        return context

    def post(self, request, *args, **kwargs):
        form = request.POST
        if form.get('entry_pk'):
            entry = Entry.objects.get(pk=form.get('entry_pk'))
            entry.value = form.get('entry_value')
            entry.save()
        else:
            subpdo = SubPDO.objects.get(pk=form.get('subpdo_pk'))
            if form.get('comment'):
                subpdo.comments = form.get('comment')
            else:
                subpdo.detailed_data_src = form.get('data_src')
            subpdo.save()

        return redirect('project', pk=self.get_object().pk)
