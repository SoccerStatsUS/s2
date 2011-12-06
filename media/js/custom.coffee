$(document).ready( ->

  # Can't get tablesorter to work...
  createSortLoader = (div) ->
    d = $("table", div)
    () -> d.tablesorter()



  getLineups = ->
    lineups_div = $("#lineups")
    if lineups_div.length
      opts = $("#lineup_form").serialize()
      console.log opts
      url = "/lineups/ajax?#{opts}"
      lineups_div.load(url)


  $("#lineup_form").keyup getLineups
  getLineups()



  getStats = ->
    stats_div = $("#stats")
    if stats_div.length
      opts = $("#stat_form").serialize()
      console.log opts
      url = "/stats/ajax?#{opts}"
      stats_div.load(url)

  $("#stat_form").keyup getStats
  getStats()



)
