var initFunc = function ()
{
	$.getJSON('/Fall 2012.json', loadSemesterJson);
};

function loadSemesterJson(semester_data) {
  var courses_array = [];
	for(course in semester_data) {
    courses_array.push(course);
  }
  courses_array.sort();

  for (var i = 0; i < courses_array.length; i++) {
    var course = courses_array[i];
		$("#chartSelect").append(new Option(course, course));
	}
	
	$("#chartSelect").change(
		function () {
			var newChartName = $("#chartSelect").val();
			var course_data = semester_data[newChartName];
			
			var graphs = [];
			for (var i=0; i < course_data.length; i++) {
				var question = course_data[i];
				var labels = [];
				var data = [];
				for (var j = 0; j < question.answers.length; j++) {
					var item = question.answers[j];
					labels.push(item[0]);
					data.push(item[1]);
				}
				graphs.push({title: question.prompt, data:{datasets:[{data: data}], labels: labels}});
			}
			spawnCanvas(newChartName, graphs);
		}
	);
}


function prettyCourseName(name)
{
    var dept = name.match(/\D+/);
    var num = name.match(/\d+/);
    return dept[0].toUpperCase() + ' ' + num[0];
}


$(document).ready(initFunc);
