import datetime

from django.core.paginator import Paginator
from django.db import models
from django.db.models import F, Max, Min
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from transactions.forms import TransactionForm
from transactions.models import Transaction


def transaction_index(request):

    # nulls_last keeps the undated transactions from heading the table.
    transactions = Transaction.objects.select_related('person', 'team_to').order_by(
        F('date').desc(nulls_last=True))

    form = TransactionForm(request.GET)
    ttype = ''

    if form.is_valid():
        ttype = form.cleaned_data['ttype']
        if ttype:
            transactions = transactions.filter(ttype=ttype)

    bounds = transactions.aggregate(first=Min('date'), last=Max('date'))
    page = Paginator(transactions, 100).get_page(request.GET.get('page'))

    context = {
        'transactions': page.object_list,
        'page': page,
        'form': form,
        'ttype': ttype,
        'first_date': bounds['first'],
        'last_date': bounds['last'],
        }

    return render(request, "transactions/index.html",
                              context)


def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction,
        }
    return render(request, "transactions/detail.html",
                              context)
