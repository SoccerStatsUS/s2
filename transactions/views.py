import datetime

from django.db import models
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from transactions.models import Transaction


def transaction_index(request):

    # nulls_last keeps the 41 undated transactions from heading the table.
    transactions = Transaction.objects.select_related('person', 'team_to').order_by(
        F('date').desc(nulls_last=True))
    dated = transactions.exclude(date=None)

    context = {
        'transactions': transactions,
        'transaction_count': transactions.count(),
        'first_date': dated.last().date if dated.exists() else None,
        'last_date': dated.first().date if dated.exists() else None,
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
