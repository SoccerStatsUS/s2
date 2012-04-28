from django.contrib import admin

from teams.models import Team

class TeamAdmin(admin.ModelAdmin):
    display_fields = ('short_name', 'slug', 'founded', 'city', )
    list_filter = ('real', 'defunct')
    search_fields = ('short_name', 'name', 'city')


admin.site.register(Team, TeamAdmin)

