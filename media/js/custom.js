(function() {
  $(document).ready(function() {
    var createSortLoader, getLineups, getStats, getTeams, hash, tabs;
    $("#bio").tablesorter();
    $("#player_chart").tablesorter();
    $("#competition_index").tablesorter();
    $("select").change(function() {
      var url, x;
      x = $(this).find("option:selected");
      url = x.attr("ref");
      return window.location = url;
    });
    createSortLoader = function(div) {
      var d;
      d = $("table", div);
      return function() {
        return d.tablesorter();
      };
    };
    getLineups = function() {
      var div, opts, url;
      div = $("#lineups");
      if (div.length) {
        div.html("Loading...");
        opts = $("#lineup_form").serialize();
        url = "/lineups/ajax?" + opts;
        console.log(url);
        return div.load(url);
      }
    };
    $("#submit_button").click(getLineups);
    getStats = function() {
      var div, opts, url;
      div = $("#stats");
      if (div.length) {
        div.html("Loading...");
        opts = $("#stat_form").serialize();
        console.log(opts);
        url = "/stats/ajax?" + opts;
        div.load(url);
      }
      return false;
    };
    $("#submit_button").click(getStats);
    getStats();
    getTeams = function() {
      var div, opts, url;
      div = $("#teams");
      if (div.length) {
        div.html("Loading...");
        opts = $("#team_form").serialize();
        console.log(opts);
        url = "/teams/ajax?" + opts;
        div.load(url);
      }
      return false;
    };
    $("#submit_button").click(getTeams);
    $(".bigboard li").click(function() {
      var slug;
      slug = $(this).attr("slug");
      $(".bigboard li").removeClass("red");
      $(".bigboard li[name=" + slug + "]").addClass("red");
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
    if (tabs.length) {
      $(tabs[0]).click();
    }
    hash = window.location.hash;
    if (hash) {
      return $("a[href=" + hash + "] li").click();
    }
  });
}).call(this);
