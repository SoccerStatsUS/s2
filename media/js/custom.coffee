$(document).ready( ->

  # Can't get tablesorter to work...
  createSortLoader = (div) ->
    d = $("table", div)
    () -> d.tablesorter()

  # Ajax functionality for stats/lineups/team search.
  getLineups = ->
    div = $("#lineups")
    if div.length
      div.html("Loading...")
      opts = $("#lineup_form").serialize()
      url = "/lineups/ajax?#{opts}"
      console.log url
      div.load(url)

  $("#submit_button").click getLineups

  getStats = ->
    div = $("#stats")
    if div.length
      div.html("Loading...")
      opts = $("#stat_form").serialize()
      console.log opts
      url = "/stats/ajax?#{opts}"
      div.load(url)
    return false

  $("#submit_button").click getStats
  getStats()

  getTeams = ->
    div = $("#teams")
    if div.length
      div.html("Loading...")
      opts = $("#team_form").serialize()
      console.log opts
      url = "/teams/ajax?#{opts}"
      div.load(url)
    return false

  $("#submit_button").click getTeams

  # USMNT Big Board functionality.
  $(".bigboard li").click ->
    slug = $(this).attr("slug")
    $(".bigboard li").removeClass("red")
    $(".bigboard li[name=#{ slug }]").addClass("red")
    $("#ajax_box").load("/drafts/x/#{ slug }")

  # Want to do this better.
  $("#tab_wrapper div").each ->
    tab = $(this).attr("tab")
    text = "<li>#{ tab }</li>"
    $("#tabs").append(text);

  $("#tabs li").click ->
    name = $(this).html()
    $("#tabs li").removeClass "grey"
    $(this).addClass "grey"

    $("#tab_wrapper div").each ->
      $(this).hide()
    $("#tab_wrapper div[tab=#{ name }]").show()

  tabs = $("#tabs li")
  if tabs.length
    $(tabs[0]).click()



)
