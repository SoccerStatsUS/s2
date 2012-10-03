$(document).ready( ->



  $("#bio").tablesorter()
  $("#player_chart").tablesorter()
  $("#competition_index").tablesorter()
  $("#stadium_list").tablesorter()
  $("#position_index").tablesorter()
  $("#money_index").tablesorter()
  $(".standings_list").tablesorter()

  # Competition page button selection activity
  #$("select").change ->
  #  x = $(this).find("option:selected")
  #  url = x.attr("ref")
  #  window.location = url



  # Can't get tablesorter to work...
  createSortLoader = (div) ->
    d = $("table", div)
    () -> d.tablesorter()



  makeAjaxGetter = (form, target, url) ->
    getAjax = ->
      div = $(target)
      if div.length
        div.html("Loading...")
        opts = $("#lineup_form").serialize()
        u = "{#url}?#{opts}"
      console.log url
      div.load(url)

    $("#submit_button").click getAjax
    #  getAjax()


  #getLineups = makeAjaxGetter("#lineup_form", "#lineups", "/tools/ajax/lineups")
  #getStats = makeAjaxGetter("#stat_form", "#stats", "/tools/ajax/stats")
  #getGames = makeAjaxGetter("#game_form", "#games", "/tools/ajax/games")
  #getGoals = makeAjaxGetter("#goal_form", "#goals", "/tools/ajax/goals")


  # Ajax functionality for stats/lineups/team search.
  getLineups = ->
    div = $("#lineups")
    if div.length
      div.html("Loading...")
      opts = $("#lineup_form").serialize()
      url = "/tools/ajax/lineups?#{opts}"
      console.log url
      div.load(url)

  $("#submit_button").click getLineups
  getLineups()

  getStats = ->
    div = $("#stats")
    if div.length
      div.html("Loading...")
      opts = $("#stat_form").serialize()
      console.log opts
      url = "/tools/ajax/stats?#{opts}"
      div.load(url)
    return false

  $("#submit_button").click getStats
  getStats()


  getGames = ->
    div = $("#games")
    if div.length
      div.html("Loading...")
      opts = $("#game_form").serialize()
      console.log opts
      url = "/tools/ajax/games?#{opts}"
      div.load(url)
    return false

  $("#submit_button").click getGames
  getGames()

  getGoals = ->
    div = $("#goals")
    if div.length
      div.html("Loading...")
      opts = $("#goal_form").serialize()
      console.log opts
      url = "/tools/ajax/goals?#{opts}"
      div.load(url)
    return false

  $("#submit_button").click getGoals
  getGoals()

  # USMNT Big Board functionality.
  $(".bigboard li").click ->
    slug = $(this).attr("slug")
    $(".bigboard li").removeClass("red")
    $(".bigboard li[name=#{ slug }]").addClass("red")
    $("#ajax_box").load("/drafts/x/#{ slug }")

  # Want to do this better.
  $("#tab_wrapper div").each ->
    tab = $(this).attr("tab")
    text = "<a href='\##{ tab }'><li>#{ tab }</li></a>"
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
