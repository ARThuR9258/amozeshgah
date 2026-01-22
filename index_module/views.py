from django.shortcuts import render

# Create your views here.



def first_page(request):
    return render(request, 'index_module/main_page.html')



def main_dashboard(request):
    return render(request, 'index_module/index.html')