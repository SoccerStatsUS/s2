
(function() {

  $(document).ready(function() {

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

  });
}).call(this);
