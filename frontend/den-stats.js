// This list is used to populate the semesters dropdown.
var semesters = ["Spring 2013", "Fall 2012"];

var initFunc = function ()
{
  // Load the list of semesters
  for (var i=0; i < semesters.length; i++) {
    $("#semester_select").append(new Option(semesters[i], semesters[i]));
  }
  // add a change listener
  $("#semester_select").change(semesterSelectionChanged);
};

var semesterSelectionChanged = function() {
  var new_semester = $("#semester_select").val();
  if (new_semester) { // weed out "select a semester" option
    $.getJSON(new_semester + '.json', loadSemesterJson);
  }
};

function loadSemesterJson(semester_data) {
  
  // Build a sorted list of the courses found in the semester we're loading
  var courses_array = [];
  for(course in semester_data) {
    courses_array.push(course);
  }
  courses_array.sort();

  var class_select = $('#class_select');
  
  // clear all options from the class select, then add the new options
  class_select.children().remove();
  class_select.append(new Option("Select a course", ''));
  for (var i = 0; i < courses_array.length; i++) {
    var course = courses_array[i];
    class_select.append(new Option(course, course));
  }
  
  // remove the old handler, and attach the new one
  class_select.off(); // remove all handlers
  class_select.change(
    function(){
      return classSelectChange(semester_data);
    }
  );
}

var classSelectChange = function (semester_data) {
  var newChartName = $("#class_select").val();
  if (newChartName) {
    var course_data = semester_data[newChartName];
    
    var graphs = [];
    for (var i=0; i < course_data.length; i++) {
      var question = course_data[i];

      if (question.type !== "freeform")
      {
        var labels = [];
        var data = [];
        for (var j = 0; j < question.answers.length; j++) {
          var item = question.answers[j];
          labels.push(item[0]);
          data.push(item[1]);
        }
        var graph_info = {
          title: question.prompt,
          data: {
            datasets:[{data: data}],
            labels: labels
          },
        };
        if (question.others && question.others.length > 0)
          graph_info.others = question.others;
        graphs.push(graph_info);
      } else {
        graphs.push({
          title: question.prompt,
          answers: question.answers.slice(0),
        });
      }
    }
    spawnCanvas(newChartName, graphs);
  }
};

function prettyCourseName(name)
{
    var dept = name.match(/\D+/);
    var num = name.match(/\d+/);
    return dept[0].toUpperCase() + ' ' + num[0];
}


$(document).ready(initFunc);
