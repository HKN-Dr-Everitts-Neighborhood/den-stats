#! python

import os, os.path, json
from functools import partial
from toolbox_parser import (
    toolbox_parser,
    attach_survey_info_fa12,
    attach_survey_info_sp13,
)
from summarize_data import summarize

"""
The point of this script is to turn semester-specific data formats into
something more common - namely, Survey objects.  There will be a lot of
special cases here, because this is the designated dumping ground for
the dirty logic.
"""

def google_docs_parser(folder, files):
    print "googleparse", files
    return []


# This dict tells us which parser to run for each folder (semester)
# Maintainers will probably need to add to this dict.
semester_parser = {
    "Spring 2012": google_docs_parser,
    "Fall 2012": partial(
                        toolbox_parser,
                        tech_electives_hack=True, 
                        attach_survey_info=attach_survey_info_fa12
                    ),
    "Spring 2013": partial(
                        toolbox_parser,
                        attach_survey_info=attach_survey_info_sp13
                    ),
}

def main():
    # scan raw_data directory for folders
    for folder in os.listdir("raw_data"):

        # scan each folder (semester) for data files
        full_path = os.path.join("raw_data", folder)

        # and pass them into the function designated for parsing files
        # from that semester.
        surveys = semester_parser[folder](full_path, os.listdir(full_path))

        with open(os.path.join('summarized_data', folder + '.json'), 'w') as f:
            f.write(json.dumps(summarize(surveys)))

if __name__ == "__main__":
    main()
