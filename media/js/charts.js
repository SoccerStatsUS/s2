// Simple pie chart.

var pieChart = function(selector, data){

var width = 960,
    height = 400,
    radius = Math.min(width, height) / 2;

var color = d3.scale.category20();

var arc = d3.svg.arc()
    .outerRadius(radius - 10)
    .innerRadius(0);

var pie = d3.layout.pie()
    .value(function(d) { return d[1]; });

var svg = d3.select(selector).append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

var g = svg.selectAll(".arc")
      .data(pie(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", arc)
      .style("fill", function(d,i) { return color(i); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
      .attr("dy", ".35em")
      .style("text-anchor", "middle")
      .attr("font-size", ".4em")
      .text(function(d) { return d.data[0]; });

};



// Game data +/- chart. - a la baseball-reference

var gamesChart = function(selector, data){


var margin = {top: 20, right: 20, bottom: 50, left: 50},
width = 960 - margin.left - margin.right,
height = 200 - margin.top - margin.bottom;

var x = d3.scale.ordinal().rangeRoundBands([0, width], .1, 1).domain(data.map(function(d, i) { return i; }));
var y = d3.scale.linear().range([height, 0]).domain([d3.min(data), d3.max(data)]);
var xAxis = d3.svg.axis().scale(x).orient("bottom");
var yAxis = d3.svg.axis().scale(y).orient("left")


var svg = d3.select(selector).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .attr("font-size", ".4em")
    .call(xAxis)
    .selectAll("text")  
    .style("text-anchor", "end")
    .attr("dx", ".2em")
    .attr("dy", ".8em")

svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("y", 6)
    .attr("dy", ".71em")
    .attr("dx", "1.5em")
    .style("text-anchor", "end")
    .text("+/-");

svg.append("g")
      .attr("class", "x axis")
      .append("line")
      .attr("y1", y(0))
      .attr("y2", y(0))
      .attr("x2", width);


svg.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", function(d) { return d < 0 ? "bar negative" : "bar positive"; })
    .attr("x", function(d, i) { return x(i); })
    .attr("width", x.rangeBand())
    .attr("y", function(d) { return y(Math.max(0, d)); })
    .attr("height", function(d) { return Math.abs(y(d) - y(0)); })

}


// Game calendar chart.

var calendarChart = function(selector, data){


var cdates = []
for (var i=0; i < data.length; i++){
  cdates.push(data[i][0]);                  
}


var width = 960,
    height = 136,
    cellSize = 17; 

var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    percent = d3.format(".1%"),
    format = d3.time.format("%Y-%m-%d");

var color = d3.scale.quantize()
    .domain([-.05, .05])
    .range(d3.range(11).map(function(d) { return "q" + d + "-11"; }));

var svg = d3.select(selector).selectAll("svg")
  .data(d3.range(d3.min(data, function(e){ return parseInt(e[0].split('-')[0]); }), 
                 1 + d3.max(data, function(e){ return parseInt(e[0].split('-')[0]); })))

  .enter().append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("class", "RdYlGn")
  .append("g")
    .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

svg.append("text")
    .attr("transform", "translate(-6," + cellSize * 3.5 + ")rotate(-90)")
    .style("text-anchor", "middle")
    .text(function(d) { return d; });

var rect = svg.selectAll(".day")
    .data(function(d) { return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("rect")
    .attr("class", "day")
    .attr("width", cellSize)
    .attr("height", cellSize)
    .attr("x", function(d) { return week(d) * cellSize; })
    .attr("y", function(d) { return day(d) * cellSize; })
    .datum(format);


svg.selectAll(".month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("path")
    .attr("class", "month")
    .attr("d", monthPath);

rect.filter(function(d) { return cdates.indexOf(d) > -1; }).attr("class", function(d){
    var result = data[cdates.indexOf(d)][1];
    if (result == "w"){ return "day q9-11"; }
    if (result == "t"){ return "day q4-11"; }
    if (result == "l"){ return "day q1-11"; }
});

rect.append("title")
    .text(function(d) { return d; });


function monthPath(t0) {
  var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
      d0 = +day(t0), w0 = +week(t0),
      d1 = +day(t1), w1 = +week(t1);
  return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
      + "H" + w0 * cellSize + "V" + 7 * cellSize
      + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
      + "H" + (w1 + 1) * cellSize + "V" + 0
      + "H" + (w0 + 1) * cellSize + "Z";
}

d3.select(self.frameElement).style("height", "2910px");

}


// Team attendance chart

teamAttendanceChart = function(selector, data){
var margin = {top: 20, right: 20, bottom: 130, left: 100},
width = 960 - margin.left - margin.right,
height = 450 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1, 1).domain(data.map(function(d) { return d[0]; }));

var y = d3.scale.linear()
    .range([height, 0]).domain([0, d3.max(data, function(d) { return d[1]})]);


var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")

var svg = d3.select(selector).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .attr("font-size", ".4em")
    .call(xAxis)
    .selectAll("text")  
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", function(d) {
        return "rotate(-65)" 
    });

svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("avg. attendance");

svg.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return x(d[0]); })
    .attr("width", x.rangeBand())
    .attr("y", function(d) { return y(d[1]); })
    .attr("height", function(d) { return height - y(d[1]); });

}


yearAttendanceChart = function(selector, data){

var margin = {top: 20, right: 20, bottom: 130, left: 300},
width = 960 - margin.left - margin.right,
height = 500 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1, 1).domain(data.map(function(d) { return d[0]; }));

var y = d3.scale.linear()
    .range([height, 0]).domain([0, d3.max(data, function(d) { return d[1]})]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")

var svg = d3.select(selector).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .attr("font-size", ".4em")
    .call(xAxis)
    .selectAll("text")  
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", function(d) {
        return "rotate(-65)" 
    });

svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("avg. attendance");

svg.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return x(d[0]); })
    .attr("width", x.rangeBand())
    .attr("y", function(d) { return y(d[1]); })
    .attr("height", function(d) { return height - y(d[1]); });

}




stadiumCapacityChart = function(selector, data){

var margin = {top: 80, right: 0, bottom: 10, left: 80},
    width = 500,
    height = 1500;

var leftMargin = 200; // bars margin

var x = d3.scale.linear()
          .domain([0, d3.max(data, function(e) { return e.capacity; })]).range([0, width - leftMargin])

var y = d3.scale.ordinal().rangeRoundBands([0, height], 1)
          .domain(data.map(function(d) { return d.team + " - " + d.stadium}));


var yAxis = d3.svg.axis()
    .scale(y)
    .orient("right");


var svg = d3.select(selector).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .style("margin-left", -margin.left + "px")
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "y axis")
    .attr("font-size", ".4em")
    .call(yAxis)

svg.selectAll(".box")
      .data(data).enter().append("rect")
      .attr("x", function(d){ return leftMargin; })
      .attr("y", function(d, i){ return y(d.team); })
      .attr("fill", function(d){ return "#ccc"; })
      .attr("width", function(d){ return x(d.capacity) })
      .attr("height", function(d){ return 30; })

svg.selectAll(".box")
      .data(data).enter().append("rect")
      .attr("x", function(d){ return leftMargin; })
      .attr("y", function(d, i){ return y(d.team); })
      .attr("fill", function(d){ return "#00c"; })
      .attr("width", function(d){ return x(d.attendance) })
      .attr("height", function(d){ return 30; })


}