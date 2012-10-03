from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from collections import defaultdict

from money.models import Salary
from bios.models import Bio


#@cache_page(60 * 60 * 12)
def money_index(request):
    """
    List all drafts.
    """

    context = {
        'salaries': Salary.objects.all(),
        }
    return render_to_response("money/index.html",
                              context,
                              context_instance=RequestContext(request))



def bad_money_index(request):
    """
    List all drafts.
    """

    slugs = defaultdict(int)

    context = {
        'salaries': salaries,
        }
    return render_to_response("money/index.html",
                              context,
                              context_instance=RequestContext(request))

