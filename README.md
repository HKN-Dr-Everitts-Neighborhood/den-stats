den-stats
=========

A site to display results for DEN.

The basic flow of the code here:
# Translate data to a standard format - abstract away the details of the survey system used in each semester
# Produce Summarized data.  This data reflects everything needed to draw the graphs - and nothing more.
# The frontend - draws the graphs.

Design Goals
=============

* Isolate all semester-specific / special case logic from the main parts of the code.
* Make sure that single-user responses aren't visible in the front end.  I.e. we're publishing aggregated data, and don't want to make the whole data set public - at least, not intentionally.  We may want to provide breakdowns by demographic categories - i.e. graphing freshmen/sophomore/junior/senior separately.
* The front end should be agnostic to questions - it should display what it's given, nothing more, nothing less.

Data Flow
===========

Each semester will be downloaded to the proper folder in raw_data.  This data will then be translated to files in processed_data (preprocessing / abstracting data formats), and then to files in summarized_data, which is what will be published/ consumed by the frontend code.
