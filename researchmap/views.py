# Create your views here.
import json, urllib
from django.http import HttpResponse
from ResearchMap.researchmap.models import Document
from django.template import loader, Context, RequestContext
from django import forms
from django.core.cache import cache
from ResearchMap.researchmap.plugins.scholar import ScholarQuerier, ScholarAuthorParser
from ResearchMap.researchmap.plugins.acm import ACMAuthorParser, ACMArticleParser

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
    
def markers(request):
    query = request.GET.get('q')
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' + query + '&sensor=true&key=AIzaSyCZMe3afa1hXz4v9_FzgQ6p2CrKeDGYVtQ'
    result = json.load(urllib.urlopen(url))    
    return HttpResponse(json.dumps(result['results']), mimetype='application/json')

def search(request):
    query = request.GET.get('q')
    articles_obj = cache.get('q=' + query)
    if articles_obj == None:
        querier = ScholarQuerier(count=100, year_lo=2005, year_hi=2013)
        querier.query(query)
        articles = querier.get_articles()
        # Caches query for one day
        cache.set('q=' + query, json.dumps(articles, 86400))
    else:
        articles = json.loads(articles_obj)

    author_querier_scholar = ScholarAuthorParser()
    author_querier_acm = ACMAuthorParser()
    out = []
    queried = []
    for art in articles:
        # Find additional information from ACM
        #if art['URL'].startswith('http://dl.acm.org/citation.cfm'):
        #    article_querier = ACMArticleParser()
        #    article_obj = cache.get(art['URL'])
        #    if article_obj == None:
        #        article_querier.query(art['URL'])
        #        article_obj = article_querier.article.as_obj()
        #        # Caches article for one week
        #        cache.set(art['URL'], json.dumps(article_obj), 604800)
        #    else:
        #        article_obj = json.loads(article_obj)
        #    
        #    # Replace all authors 
        #    # TODO: Implement a merge system
        #    art['Authors'] = article_obj['Authors']

        # Replace author information
        for author in art['Authors']:
            if author['url'] not in queried:
                author_obj = cache.get(author['url'])
                if author_obj == None:
                    if author['url'].startswith('http://dl.acm.org/author_page.cfm'):
                        author_querier = author_querier_acm
                    else:
                        author_querier = author_querier_scholar

                    author_querier.query(author['url'])
                    author_obj = author_querier.author.as_obj()
                    if author_obj['Name'] == None:
                        author_obj['Name'] = author[author['name']]

                    # Caches author for one week
                    cache.set(author['url'], json.dumps(author_obj), 604800)
                else:
                    author_obj = json.loads(author_obj)

                out.append(author_obj)
                queried.append(author['url'])

    return HttpResponse(json.dumps(out, sort_keys=True, indent=2, separators=(',', ': ')))

    
