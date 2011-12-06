(function() {
  $(document).ready(function() {
    var createSortLoader, getLineups, getStats;
    createSortLoader = function(div) {
      var d;
      d = $("table", div);
      return function() {
        return d.tablesorter();
      };
    };
    getLineups = function() {
      var lineups_div, opts, url;
      lineups_div = $("#lineups");
      if (lineups_div.length) {
        opts = $("#lineup_form").serialize();
        console.log(opts);
        url = "/lineups/ajax?" + opts;
        return lineups_div.load(url);
      }
    };
    $("#lineup_form").keyup(getLineups);
    getLineups();
    getStats = function() {
      var opts, stats_div, url;
      stats_div = $("#stats");
      if (stats_div.length) {
        opts = $("#stat_form").serialize();
        console.log(opts);
        url = "/stats/ajax?" + opts;
        return stats_div.load(url);
      }
    };
    $("#stat_form").keyup(getStats);
    return getStats();
  });
}).call(this);
