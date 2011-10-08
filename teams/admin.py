from s2.teams.models import Team
from django.contrib import admin

class TeamAdmin(admin.ModelAdmin):
    display_fields = ('short_name', 'slug', 'founded', 'city', )
    list_filter = ('real', 'defunct')
    search_fields = ('short_name', 'name', 'city')


admin.site.register(Team, TeamAdmin)

