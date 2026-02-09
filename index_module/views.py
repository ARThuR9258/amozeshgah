from django.shortcuts import render
from account_module.decorators import admin_required

# Create your views here.



def first_page(request):
    return render(request, 'index_module/main_page.html')



@admin_required
def main_dashboard(request):
    return render(request, 'index_module/index.html')