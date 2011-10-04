from s2.bios.models import Bio



def person_list_generic(request, person_list):
    context =  {
        "people": person_list,
        }
    return render_to_response("players/index.html",
                              context,
                              context_instance=RequestContext(request)
                              )    


def person_index(request):
    people = Person.objects.all()
    return person_list_generic(request, people)


def person_detail(request, slug):
    person = Bio.objects.get(slug=slug)
    context = {
        "person": person,
        }
    return render_to_response("players/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   
