den-stats
=========

A site to display results for DEN.

Design Goals
=============

* Isolate all semester-specific / special case logic from the main parts of the code.
* Make sure that single-user responses aren't visible in the front end.  I.e. we're publishing aggregated data, and don't want to make the whole data set public - at least, not intentionally.  We may want to provide breakdowns by demographic categories - i.e. graphing freshmen/sophomore/junior/senior separately.
* The front end should be agnostic to questions and pecularities of each semester's surveys - it should display what it's given, nothing more, nothing less.

Data Flow
===========

Each semester will be downloaded to the proper folder in raw_data.  When backend/preprocess.py is run,
this data will then be translated to python objects (Surveys and Questions in backend/survey_obj.py) by
semester and survey-platform specific code. From these intermediate python objects, the data is then
summarized, forming the json files in the summarized_data folder.

Deploying
===========

To completely deploy everything:

* Attach the javascript files in frontend/ to the wiki
* Attach the json files from summarized_data/ to the wiki
* Take the body of displayChart.html, and copy-paste it onto the wiki.
Rewrite the external scripts src's to point to the js attachments.
* Make sure the wiki version is able to load the json files.  This is simply
a matter of the javascript getting the path right.  This could be a problem if
you create a new page for the surveys (instead of the current one).

Dev Notes
==========

Currently, the best way to test is to run

```
python -m SimpleHTTPServer
```

From within the frontend folder.  Copy the generated .json files from summarized_data
into the frontend folder, and then open displayChart.html in a browser. 
