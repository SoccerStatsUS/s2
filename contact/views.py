from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from contact.forms import ContactForm
from django.urls import reverse

@csrf_exempt
def contact_index(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            if form.cleaned_data['name']:
                subject = "Spam from %s" % form.cleaned_data['email']
            else:
                subject = "Contact from %s" % form.cleaned_data['email']
            send_mail(subject, form.cleaned_data['message'], form.cleaned_data['email'], ['chris@socceroutsider.com'], fail_silently=False)
            return HttpResponseRedirect(reverse('contact_thanks'))

    else:
        form = ContactForm()

    context = {
        'form': form,
    }

    return render(None, 'contact/index.html', 
                              context)



def contact_thanks(request):
    return render(None, 'contact/thanks.html', 
                              {})
