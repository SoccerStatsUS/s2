(function() {

  $(document).ready(function() {

      $("#bio").tablesorter();
      $("#player_chart").tablesorter();
      $("#competition_index").tablesorter();
      $("#stadium_list").tablesorter();
      $("#position_index").tablesorter();
      $("#money_index").tablesorter();
      $(".standings_list").tablesorter();
      
      $(".bigboard li").click(function() {
          var slug = $(this).attr("slug");
          $(".bigboard li").removeClass("red");
          $(".bigboard li[slug=" + slug + "]").addClass("red");
          return $("#ajax_box").load("/drafts/x/" + slug);
      });


      // Turn this into a factory.
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

          //
          tabsLI.click(function() {
              var name = $(this).html();
              tabsLI.removeClass("grey");
              $(this).addClass("grey");
              tabWrapper.children("div").each(function() {
                  return $(this).hide();
              });
              tabWrapper.children("div[tab=" + name + "]").show();
              return false;
          });

          if (tabsLI.length) {
              return $(tabsLI[0]).click();
          };
      };

      makeTab("#tabs", "#tab_wrapper");
      makeTab("#stat-tabs", "#stat-tab-wrapper");
      makeTab("#standing-tabs", "#standing-tab-wrapper");


  });
}).call(this);
