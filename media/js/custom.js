(function() {
  $(document).ready(function() {
    var drawChart;
    google.load('visualization', '1.0', {
      'packages': ['corechart']
    });
    google.setOnLoadCallback(drawChart);
    return drawChart = function() {
      var chart, data, options;
      data = new google.visualization.DataTable();
      data.addColumn('string', 'Topping');
      data.addColumn('number', 'Slices');
      data.addRows([['Mushrooms', 3], ['Onions', 1], ['Olives', 1], ['Zucchini', 1], ['Pepperoni', 2]]);
      options = {
        title: 'How Much Pizza I Ate Last Night',
        width: 400,
        height: 400
      };
      return chart = new google.visualization.PieChart($("#chart_div"));
    };
  });
}).call(this);
