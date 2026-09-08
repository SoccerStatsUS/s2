from competitions.models import Competition, Season
from teams.models import Team


def get_blurb_target(blurb):
    if blurb["kind"] == "competition":
        return Competition.objects.get(name=blurb["competition"])
    if blurb["kind"] == "season":
        return Season.objects.get(
            competition__name=blurb["competition"],
            name=blurb["season"],
        )
    if blurb["kind"] == "team":
        return Team.objects.get(name=blurb["team"])
    raise ValueError("unknown blurb kind: %s" % blurb["kind"])
