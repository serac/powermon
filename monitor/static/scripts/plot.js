// Plots a data series in flot JSON format in the given container to hold the plot.
function plotSeries(jsonUrl, plot_container) {
  var options = {
    series: {
      lines: { show: true, fill: false, lineWidth: 1}
    },
    xaxis: { mode: "time", twelveHourClock: false },
    legend: {
      backgroundOpacity: 0,
      noColumns: 2,
    }
  };

  $.getJSON(jsonUrl, function (json) {
    $.plot(plot_container, json, options);
  });
}
