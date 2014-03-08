
(function() {

  $(document).ready(function() {

      $(".stats").tablesorter();
      $(".standings").tablesorter();

      //$("#tab_wrapper").hide();
      //$("#sub-tab-wrapper").hide();

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
              tabsLI.removeClass("active");
              $(this).addClass("active");
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

      $("#header").click(function(){
          var m = $("#menu");
          var mb = $("#menu-button");
          var display = ((m.css("display") === "none") ? "block" : "none");
          m.css("display", display);
          if (mb.css("color") === "rgb(255, 255, 255)"){
          mb.css("color", "#000").css("background-color", "#fff");
          } else {
          mb.css("color", "#fff").css("background-color", "#000");
          }
      });

      if (window.location.hash === "#menu"){
          $("#header").click();
      };

      makeTab("#tabs", "#tab_wrapper");
      makeTab("#subtabs", "#subtab_wrapper");
      makeTab("#subtabs2", "#subtab_wrapper2");

  });
}).call(this);
