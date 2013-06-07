# Create your views here.
import json, urllib
from django.http import HttpResponse
from ResearchMap.researchmap.models import Document
from django.template import loader, Context, RequestContext
from django import forms
from django.core.cache import cache
from ResearchMap.researchmap.plugins.scholar import ScholarQuerier, ScholarAuthorParser


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
    c = RequestContext(request, {
        'docs': docs,
        'form': form
    })
    response = HttpResponse(t.render(c))
    response['Access-Control-Allow-Origin'] = "*"
    return response

#Form index filters
class SearchForm(forms.Form):
    s = forms.CharField(label = "Search for keyword")
    action = "/"    
    
def markers(request, query):
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' + query + '&sensor=true&key=AIzaSyCZMe3afa1hXz4v9_FzgQ6p2CrKeDGYVtQ'
    result = json.load(urllib.urlopen(url))    
    return HttpResponse(json.dumps(result['results']), mimetype='application/json')

def scholar(request, query):
    querier = ScholarQuerier(count=100, year_lo=2005, year_hi=2013)
    author_querier = ScholarAuthorParser()
    querier.query(query)
    articles = querier.articles
    out = []

    queried = []

    for art in articles:
        # Replace author information
        for author in art['authors']:
            if author['url'] not in queried:
                author_obj = cache.get(author['url'])
                if author_obj == None:
                    author_querier.query(author['url'])
                    author_obj = author_querier.author.as_obj()
                    cache.set(author['url'], json.dumps(author_obj), 86400)
                else:
                    author_obj = json.loads(author_obj)

                out.append(author_obj)
                queried.append(author['url'])

    return HttpResponse(json.dumps(out, sort_keys=True, indent=2, separators=(',', ': ')))

    
