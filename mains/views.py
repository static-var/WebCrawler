from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from urllib.parse import urlsplit
from Basics import *

# Create your views here.
def homeCall(request):
    return render_to_response("index.html")

def websiteName(request):
    # The URL given
    webSite = request.POST['website']
    webSite = domainName(webSite)
