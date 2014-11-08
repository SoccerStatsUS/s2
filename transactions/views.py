import datetime

from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from transactions.models import Transaction


def transaction_index(request):

    transactions = Transaction.objects.all()
    context = {
        'tranactions': transactions,
        }

    return render_to_response("transactions/index.html",
                              context,
                              context_instance=RequestContext(request))


def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction,
        }
    return render_to_response("transactions/detail.html",
                              context,
                              context_instance=RequestContext(request))
