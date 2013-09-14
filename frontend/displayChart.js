var whiteRGB = "#000000";

var cWidth = 800;
var cHeight = 350;

var CanvasChart = function (canvasElem) {
  this.canvas = canvasElem;
  this.chart = new Chart(canvasElem.getContext("2d"));
};

CanvasChart.prototype.displayData = function (data) {
  var steps=8;
  var max;
  for (var i=0; i < data.datasets.length; i++)
  {
    var dataset_data = data.datasets[i].data;
    for (var j=0; j < dataset_data.length; j++)
    {
      if (max === undefined)
        max = dataset_data[j];
      else
        max = Math.max(dataset_data[j], max);
    }
  }

  // prune if too many unused answer choices
  // Note: this only properly supports the single dataset case.
  if (data.datasets[0].data.length > 10)
  {
    var dataset0 = data.datasets[0];
    var new_data = [];
    var new_labels = [];
    for (var j=0; j < dataset0.data.length; j++) {
      if (dataset0.data[j] > 0) {
        new_data.push(dataset0.data[j]);
        new_labels.push(data.labels[j]);
      }
    }

    data.datasets[0].data = new_data;
    data.labels = new_labels;
  }

  var step_size = Math.ceil(max/steps);
  // minimum step size of 1, just incase we have graph with no data.
  step_size = (step_size > 0) ? step_size : 1;
  opts = {
    scaleOverride: true,
    scaleSteps: steps,
    scaleStepWidth: step_size,
    scaleStartValue: 0
  };
  this.chart.Bar(data, opts);
};

// This function is ill-named.  Though it does create canvases, it also handles others and freeform answers.
function spawnCanvas(chartName, chartData) {  
  $("#canvasDiv").html('');
  for(var i = 0; i < chartData.length; i++) {

    var newDiv = document.createElement("div")
    var newH = $("<h2></h2>").append(chartData[i].title);

    newDiv.appendChild(newH[0]);
    
    if (chartData[i].data) {
      var newCanvas = document.createElement('canvas');
      newCanvas.width = cWidth;
      newCanvas.height = cHeight;
      
      newDiv.appendChild(newCanvas);

      // caching these canvases may be a good idea in the future,
      // but let's avoid premature optimization for now.
      var chart_canvas = new CanvasChart(newCanvas);
      chart_canvas.displayData(chartData[i].data);
    }
    if (chartData[i].others) {
      var others_title = document.createElement("h4")
      others_title.innerText = "Others:";
      newDiv.appendChild(others_title);

      var new_ul = document.createElement("ul");
      var raw_responses = chartData[i].others;
      for (var j = 0; j < raw_responses.length; j++) {
        var r = raw_responses[j];

        var new_li = document.createElement("li");
        new_li.innerText = r;
        new_ul.appendChild(new_li);
      }
      newDiv.appendChild(new_ul);
    }
    if (chartData[i].answers)  {
      var raw_responses = chartData[i].answers;
      for (var j = 0; j < raw_responses.length; j++) {
        var r = raw_responses[j];

        var new_p = document.createElement("p");
        new_p.innerText = r;
        newDiv.appendChild(new_p);
      }
      if (raw_responses.length === 0) {
        var new_p = document.createElement("p");
        new_p.innerText = "No responses to display.";
        newDiv.appendChild(new_p);
      }
    }
    $("#canvasDiv").append(newDiv);
  }
};

function paintCanvas(canvasElem, fillColorString) {
  var ctxContext = canvasElem.getContext("2d");
  ctxContext.fillStyle = fillColorString;
  ctxContext.fillRect(0, 0, cWidth, cHeight);
  ctxContext.fillColorString = whiteRGB;
}

