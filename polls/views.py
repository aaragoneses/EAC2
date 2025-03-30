from django.http import HttpResponse


def index(request):
    return HttpResponse("Este es el index de los Polls del EAC2.")
