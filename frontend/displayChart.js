
// TODO: shouldn't be hardcoded.
var chartNames = ["cs225", "ece110"];

var chartCanvases = {};
var whiteRGB = "#000000";

var cWidth = 400;
var cHeight = 400;

function CanvasChart(canvasElem) {
	this.canvas = canvasElem;
	this.chart = new Chart(canvasElem.getContext("2d"));
}

CanvasChart.prototype.displayData = function (data, opts) {
	this.chart.Bar(data, opts);
}

$(document).ready(readyFunc) ;

function readyFunc() {
	populateChartSelect();

	var chartName = $("#chartSelect").val();
	var chartAllData = genChartData(chartName);
	spawnCanvas(chartName, chartAllData);

	$("#chartSelect").change(
		function () {
			var newChartName = $("#chartSelect").val();
			spawnCanvas(newChartName, genChartData(newChartName));
		}
		);
}

function populateChartSelect() {
	for(var i = 0; i < chartNames.length; i++) {
		$("#chartSelect").append(new Option(chartNames[i], chartNames[i]));
	}
}

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

