$(document).ready( ->

  # Can't get tablesorter to work...
  createSortLoader = (div) ->
    d = $("table", div)
    () -> d.tablesorter()



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




)
