(function() {

  $(document).ready(function() {
    var createSortLoader, getGames, getGoals, getLineups, getStats, makeAjaxGetter, tabs;
    $("#bio").tablesorter();
    $("#player_chart").tablesorter();
    $("#competition_index").tablesorter();
    $("#stadium_list").tablesorter();
    $("#position_index").tablesorter();
    $("#money_index").tablesorter();
    $(".standings_list").tablesorter();
    createSortLoader = function(div) {
      var d;
      d = $("table", div);
      return function() {
        return d.tablesorter();
      };
    };
    makeAjaxGetter = function(form, target, url) {
      var getAjax;
      getAjax = function() {
        var div, opts, u;
        div = $(target);
        if (div.length) {
          div.html("Loading...");
          opts = $("#lineup_form").serialize();
          u = "{#url}?" + opts;
        }
        console.log(url);
        return div.load(url);
      };
      return $("#submit_button").click(getAjax);
    };
    getLineups = function() {
      var div, opts, url;
      div = $("#lineups");
      if (div.length) {
        div.html("Loading...");
        opts = $("#lineup_form").serialize();
        url = "/tools/ajax/lineups?" + opts;
        console.log(url);
        return div.load(url);
      }
    };
    $("#submit_button").click(getLineups);
    getLineups();
    getStats = function() {
      var div, opts, url;
      div = $("#stats");
      if (div.length) {
        div.html("Loading...");
        opts = $("#stat_form").serialize();
        console.log(opts);
        url = "/tools/ajax/stats?" + opts;
        div.load(url);
      }
      return false;
    };
    $("#submit_button").click(getStats);
    getStats();
    getGames = function() {
      var div, opts, url;
      div = $("#games");
      if (div.length) {
        div.html("Loading...");
        opts = $("#game_form").serialize();
        console.log(opts);
        url = "/tools/ajax/games?" + opts;
        div.load(url);
      }
      return false;
    };
    $("#submit_button").click(getGames);
    getGames();
    getGoals = function() {
      var div, opts, url;
      div = $("#goals");
      if (div.length) {
        div.html("Loading...");
        opts = $("#goal_form").serialize();
        console.log(opts);
        url = "/tools/ajax/goals?" + opts;
        div.load(url);
      }
      return false;
    };
    $("#submit_button").click(getGoals);
    getGoals();
    $(".bigboard li").click(function() {
      var slug;
      slug = $(this).attr("slug");
      $(".bigboard li").removeClass("red");
      $(".bigboard li[slug=" + slug + "]").addClass("red");
      return $("#ajax_box").load("/drafts/x/" + slug);
    });
    $("#tab_wrapper div").each(function() {
      var tab, text;
      tab = $(this).attr("tab");
      text = "<a href='\#" + tab + "'><li>" + tab + "</li></a>";
      return $("#tabs").append(text);
    });
    $("#tabs li").click(function() {
      var name;
      name = $(this).html();
      $("#tabs li").removeClass("grey");
      $(this).addClass("grey");
      $("#tab_wrapper div").each(function() {
        return $(this).hide();
      });
      return $("#tab_wrapper div[tab=" + name + "]").show();
    });
    tabs = $("#tabs li");
    if (tabs.length) return $(tabs[0]).click();
  });

}).call(this);
