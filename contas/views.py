from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm
from django.utils.translation import gettext_lazy as _

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = SignupForm()

    return render(request, 'contas/signup.html', {
        'form': form
    })
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("login", "").strip()
        senha = request.POST.get("senha", "").strip()
        
        if not username or not senha:
            return render(request, 'contas/login.html', {'erro': 'Login e senha são obrigatórios!'})
        
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            return redirect('core:home')
        return render(request, 'contas/login.html', {'erro': 'Login ou senha incorretos!'})
    return render(request, 'contas/login.html')

def logout_view(request):
    logout(request)
    return redirect('contas:login')


