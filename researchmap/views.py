# Create your views here.
from django.http import HttpResponse
from ResearchMap.researchmap.models import Document
from django.template import loader, Context
from django import forms
import json

def home(request):
    form = SearchForm(request.GET) # Filter form
    if form.is_valid():
        s = form.cleaned_data['s']
        if s != '':
            # Search for Documents            
            docs = Document.objects.filter(title__icontains = s)
        else:
            docs = Document.objects.all()
    else:
        docs = []
        
        
    t = loader.get_template('home.html')
    c = Context({
        'docs': docs,
        'form': form
    })
    return HttpResponse(t.render(c))

#Form index filters
class SearchForm(forms.Form):
    s = forms.CharField(label = "Search for keyword")
    action = "/"    
    
def markers(request):
    output = [{'Title':'Artigo 1','Latitude':9,'Longitude':15},
              {'Title':'Artigo 2','Latitude':12,'Longitude':12},
              {'Title':'Artigo 3','Latitude':20,'Longitude':8},
              {'Title':'Artigo 4','Latitude':-40,'Longitude':1},
              {'Title':'Artigo 5','Latitude':-20,'Longitude':30},
              {'Title':'Artigo 6','Latitude':12,'Longitude':18}]
    return HttpResponse(json.dumps(output), mimetype='application/json')
    