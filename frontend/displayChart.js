var chartCanvases = {};
var whiteRGB = "#000000";

var cWidth = 400;
var cHeight = 300;

var CanvasChart = function (canvasElem) {
	this.canvas = canvasElem;
	this.chart = new Chart(canvasElem.getContext("2d"));
};

CanvasChart.prototype.displayData = function (data) {
  var steps=10;
  var max;
  for (var i=0; i < data.datasets.length; i++)
  {
    var dataset_data = data.datasets[i].data;
    for (var j=0; j < dataset_data.length; j++)
    {
      if (max === undefined)
        max = dataset_data[i];
      else
        max = Math.max(dataset_data[i], max);
    }
  }

  opts = {
    scaleOverride: true,
    scaleSteps: steps,
    scaleStepWidth: Math.ceil(max/steps),
    scaleStartValue: 0
  };
	this.chart.Bar(data, opts);
};


function spawnCanvas(chartName, chartData) {
	console.log(chartName);
	console.log(chartData);
	
	$("#canvasDiv").html('');
	for(var i = 0; i < chartData.length; i++) {
		var newCanvas = document.createElement('canvas');
		newCanvas.width = cWidth;
		newCanvas.height = cHeight;

		var newDiv = document.createElement("div")
		var newPar = $("<p></p>").append($("<h1></h1>").append(chartData[i].title));
		newDiv.appendChild(newPar[0]);
		newDiv.appendChild(newCanvas);
		$("#canvasDiv").append(newDiv);

		chartCanvases[chartName] = new CanvasChart(newCanvas);
		console.log("DATA:", chartData[i].data);
		chartCanvases[chartName].displayData(chartData[i].data);
	}
}

function paintCanvas(canvasElem, fillColorString) {
	var ctxContext = canvasElem.getContext("2d");
	ctxContext.fillStyle = fillColorString;
	ctxContext.fillRect(0, 0, cWidth, cHeight);
	ctxContext.fillColorString = whiteRGB;
}

