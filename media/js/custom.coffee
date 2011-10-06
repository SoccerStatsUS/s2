$(document).ready( ->
  google.load('visualization', '1.0', {'packages':['corechart']})

  # Set a callback to run when the Google Visualization API is loaded.
  google.setOnLoadCallback drawChart

  # Callback that creates and populates a data table,
  # instantiates the pie chart, passes in the data and
  # draws it.
  drawChart = ->
    # Create the data table.
    data = new google.visualization.DataTable()
    data.addColumn('string', 'Topping')
    data.addColumn('number', 'Slices')

    data.addRows [
      ['Mushrooms', 3],
      ['Onions', 1],
      ['Olives', 1],
      ['Zucchini', 1],
      ['Pepperoni', 2]
    ]


    # Set chart options
    options =
      title: 'How Much Pizza I Ate Last Night'
      width: 400
      height: 400

    # Instantiate and draw our chart, passing in some options.
    chart = new google.visualization.PieChart $("#chart_div")
    #chart.draw(data, options)

)
