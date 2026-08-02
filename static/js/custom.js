(function() {

  $(document).ready(function() {

      $(".stats").tablesorter();
      $(".standings").tablesorter();

      $("#search_button").click(function(){
          $("#search_form").submit();
      });

      var navSearch = $("#nav-search");
      var navSearchInput = navSearch.find("input");

      navSearch.find("button").click(function(e){
          if (!navSearch.hasClass("open")) {
              e.preventDefault();
              navSearch.addClass("open");
              navSearchInput.focus();
          } else if (!$.trim(navSearchInput.val())) {
              e.preventDefault();
              navSearch.removeClass("open");
          }
      });

      navSearchInput.on("keydown", function(e){
          if (e.which === 27) {
              navSearch.removeClass("open");
              navSearch.find("button").focus();
          }
      });

      $(document).on("click", function(e){
          if (navSearch.hasClass("open") && !$(e.target).closest("#nav-search").length) {
              navSearch.removeClass("open");
          }
      });

      var makeTab = function(containerID, wrapperID){

          var tabb = $(containerID);
          var tabWrapper = $(wrapperID);

          if ((tabb === undefined) || (tabWrapper === undefined)){
              return;
          }

          tabb.addClass("tabbing");

          // Assign tab data to the tab container
          tabWrapper.children("div").each(function() {
              var tab = $(this).attr("tab");
              if (tab !== undefined){
                  var text = "<a href='\#" + tab + "'><li>" + tab + "</li></a>";
                  tabb.append(text);
              }
          });

          // access newly created li's.
          var tabsLI = tabb.find("li")

          tabsLI.click(function() {
              var name = $(this).html();
              tabsLI.removeClass("active");
              $(this).addClass("active");
              tabWrapper.children("div").each(function() {
                  return $(this).hide();
              });
              tabWrapper.children("div[tab='" + name + "']").show();
              return false;
          });

          if (tabsLI.length) {
              return $(tabsLI[0]).click();
          };
      };

      makeTab("#tabs", "#tab_wrapper");
      makeTab("#subtabs", "#subtab_wrapper");
      makeTab("#subtabs2", "#subtab_wrapper2");

  });
}).call(this);
