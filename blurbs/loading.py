from competitions.models import Competition, Season
from teams.models import Team


def get_blurb_target(blurb):
    """Return the object a blurb attaches to, or None if it isn't loaded."""

    try:
        if blurb["kind"] == "competition":
            return Competition.objects.get(name=blurb["competition"])
        if blurb["kind"] == "season":
            return Season.objects.get(
                competition__name=blurb["competition"],
                name=blurb["season"],
            )
        if blurb["kind"] == "team":
            return Team.objects.get(name=blurb["team"])
    except (Competition.DoesNotExist, Season.DoesNotExist, Team.DoesNotExist):
        return None

    raise ValueError("unknown blurb kind: %s" % blurb["kind"])
