from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views import generic

from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response


from store.models import Book, Author
from django.core.mail import send_mail

from store.forms import ContactForm, LoginForm
#from store.tags import *

from django.contrib.auth.models import User
from jsonview.decorators import json_view

from store.search import *
from store.serializer import *

#class SearchForm(forms.Form):
#	search_by = forms.ChoiceField()
#	search_by.label = "Search by"
#	search_by.required = True
#	search_for = forms.CharField()
#	search_for.label = "Search for"
#	search_for.required = True

#def index(request):
#    if request.method == 'POST':
#        form = LoginForm(request.POST)
#        if form.is_valid():
#            return HttpResponseRedirect('/ok')
#    else:
#        form = LoginForm()
#
#    return render(request, 'store/index.html', { 'form': form })

def login_user(request):
    state = "Please login below..."
    username = password = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in."
            else:
                state = "Your account is not active."
        else:
            state = "Your username / password is not correct."

    return render_to_response('store/auth.html',
                              {'state': state, 'username': username},
                              context_instance = RequestContext(request))

def email_send(request):
    this_id = request.GET.get('id', 'NO USER SPECIFIED')
    bookname = request.GET.get('book', 'NO BOOK SPECIFIED')
    reply_email = request.POST.get('reply_email','NO REPLY EMAIL PROVIDED')
    phone = request.POST.get('phone','NO PHONE NUMBER PROVIDED')
    availability = request.POST.get('availability','NO AVAILIBILITY PROVIDED')
    message = request.POST.get('message','NO MESSAGE PROVIDED')
    user = User.objects.get(id=this_id)
    email = user.email
    subject = 'Buchladen: Someone is interested in your book "'+bookname+'"!'
    message = message+"\n\n\nTO REPLY TO THIS USER, USE THE PROVIDED EMAIL: "+reply_email+"\nOR CONTACT THEM AT THIS PHONE NUMBER: "+phone+'\n\nUSER\'S AVAILABILITY: "'+availability+'"'
    #send_mail(subject, message, 'noreply@buchladen.uwinsocr.ca',[email], fail_silently=False);
    return render_to_response('store/email-sent.html', context_instance = RequestContext(request))
        

@json_view
def search_view(request, search_terms):
    print("Searching for: %s" % search_terms)
    results = list(Search(SearchTerms(search_terms)).results())
    print("Returned " + str(results))
    book_serial = BookSerializer()
    return book_serial.list_deflate(results)

@json_view
def most_recent(request, n):
    print("Searching for: %d most recent books" % int(n))
    results = list(Book.objects.order_by('date_added').reverse()[:int(n)])
    print("Returned " + str(results))
    book_serial = BookSerializer()
    return book_serial.list_deflate(results)
