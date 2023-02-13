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

from .models import Project


class IndexView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'baseApp/index.html'


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


class ProjectView(DetailView):
    model = Project
    context_object_name = 'project'
    template_name = 'baseApp/project.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        cf = self.get_object().collection_freq
        context["project_yearly_entries"] = [
            f"{cf.prefix} {count}" for count in range(1, cf.value+1)
            ]
        return context
        