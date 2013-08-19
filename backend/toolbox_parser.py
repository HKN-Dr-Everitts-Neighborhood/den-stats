import csv, os.path
from bs4 import BeautifulSoup
from collections import defaultdict

from survey_obj import (
    Survey,
    Question,
    Other,
)

def toolbox_parser(folder, files, attach_survey_info, tech_electives_hack=False):
    '''
    Returns a dict mapping each class name (i.e. "ECE 110") to a Survey object.
    '''

    # group together files with the same name but different extensions
    title_to_files = defaultdict(list)
    for f in files:
        if f != '.gitignore':
            title_to_files[f.rsplit('.', 1)[0]].append(f)

    # Loop over all surveys
    title_to_survey = dict()
    for title in title_to_files:
        files = title_to_files[title]
        assert sorted(files) == [ title + '.csv', title + '.html' ], (
            "Missing a file for '%s'" % title
        )

        # Create the Survey object.
        survey = Survey()

        # parse the html file
        with open(os.path.join(folder, title + ".html")) as html_file:
            soup = BeautifulSoup(html_file)
        
        # parse the csv.
        with open(os.path.join(folder, title + ".csv")) as csv_file:
            lines = [line for line in csv.reader(csv_file)]

        header = lines[0]
        responses = lines[1:]
        lines = None
        
        # question_info will be a list of the headers for each question.
        question_info = defaultdict(list)
        col_to_question = [] # maps column number to question number
        for heading in header:
            # example heading: "Q4:How many hours per week, on average..."
            # The second part isn't necessarily the question - for multi-choice
            # questions, it'll be an answer choice.
            qnum, text = heading.split(':',1)
            num = int(qnum[1:]) - 1 # Strip the Q and adjust for 0-based indices
            question_info[num].append({
                "text": text,
                "other": False,
                "other-text": False
            })
            col_to_question.append(num)

        # Now we'll create all the questions.  This draws from both the html
        # and the csv - the html tells us which options are possible,
        # and the csv allows us to infer a few more things, such as which
        # questions were multi choice (checkboxes) and which were single
        # choice (radio buttons), which supported "other", etc.
        for i, question_table in enumerate(
            soup.find_all('table', {'class': 'graph-wrapper'})
        ):
            q_info = question_info[i]
            question_el = question_table.find('th', {'class': 'detail-col1'})
            q = Question()

            if question_el is None:
                question_el = question_table.find('th', {'class': 'summary-column-1'})
                q.set_type('freeform')
            else:
                options = set()
                for answer_div in question_table.find_all(
                    'div',
                    {'class': 'detail-choices'}
                ):
                    options.add(answer_div.contents[0])
                q.set_options(options)

                if len(q_info) != 1:
                    q.set_type("multi-choice")

                    # check if the last option is really an other.
                    # TODO: verify that other must appear last.
                    if q_info[-2]['text'] + " text" == q_info[-1]['text']:
                        # This assert isn't enforced on toolbox... but I would be
                        # shocked if it failed.
                        assert "other" in q_info[-2]['text'].lower()
                        q.enable_other()
                        q_info[-2]['other'] = True
                        q_info[-1]['other-text'] = True
                else:
                    q.set_type("single-choice")
                    if "Other" in options:
                        q.enable_other()
                        q_info[-1]['other-text'] = True

            q.set_text(question_el.contents[0])
            survey.add_question(q)
        
        # Now deal with the actual data.
        for resp_num, response in enumerate(responses):
            for (col_within_q, question_num), answer in zip(streak(col_to_question), response):
                used_other = False # Figure out the point of this variable.
                if survey.get_question(question_num).type == "multi-choice":
                    q_info = question_info[question_num][col_within_q]
                    if q_info['other']:
                        other_prompt = q_info['text']
                    elif q_info['other-text']:
                        if answer == '1':
                            survey.add_answer(resp_num, question_num, other_prompt, other=answer)
                    else:
                        if answer == '1':
                            survey.add_answer(resp_num, question_num, q_info['text'])
                else:
                    # Most "other" categories will be named other because that's
                    # what is supported by the templating system in survey-scripts.
                    # TODO: check that this is valid for Fall 2012.
                    if answer.lower().startswith('other:'):
                        answer_parts = answer.split(':')
                        survey.add_answer(resp_num, question_num, answer_parts[0], other=answer_parts[1])
                    else:
                        survey.add_answer(resp_num, question_num, answer)
        
        # The tech electives hack is something we did in Fall 2012.  The basic
        # idea was that we created a few surveys which each covered about a
        # dozen technical electives at a time thus reducing the amount of
        # surveys we had to set up.  It's pretty ugly though.
        if tech_electives_hack and title.endswith(')'):
            # go over options in first question, generate sub surveys
            sub_surveys_by_class = dict()
            q0 = survey.get_question(0)
            for option in q0.options:
                sub_survey = Survey()

                # copy all questions to the new survey
                for q in survey.questions[1:]:
                    sub_survey.add_question(q.copy())

                assert all(a.question_text == b.question_text for a,b in zip(survey.questions[1:], sub_survey.questions))
                print "creating subsurvey for", option
                sub_surveys_by_class[option] = sub_survey

            # set up a response_num to subsurvey map
            rnum_to_subsurvey = dict()
            for response_num, answer, other in q0.answers:
                rnum_to_subsurvey[response_num] = sub_surveys_by_class[answer]

            # now transfer all answers
            for i, q in enumerate(survey.questions[1:]):
                for rnum, answer, other in q.answers:
                    new_q = rnum_to_subsurvey[rnum].get_question(i)
                    # sanity check
                    assert q.question_text == new_q.question_text
                    new_q.add_answer(rnum, answer, other)

            for class_name in sub_surveys_by_class:
                title = title_to_filename_chars(
                    class_name.split('-')[0].strip() + ' - DEN HKN Survey'
                )
                title_to_survey[title] = sub_surveys_by_class[class_name]
        else:
            title_to_survey[title] = survey

    for title in title_to_survey:
        survey = title_to_survey[title]
        attach_survey_info(title, survey)

    return title_to_survey.values()

def streak(l):
    '''This generator is meant as a utility. It returns a pair of the length
    of the current streak in l and the next item in l.  l must be iterable -
    a generator or a list would be fine.
    
    Example: streak([1,3,3,4,4,4,4,5]) will yield (one pair at a time) the
    sequence: (0,1), (0,3), (1,3), (0,4), (1,4), (2,4), (3,4), (0,5)
    '''

    # This object is only important in that it is a unique object that can't
    # be an element returned by l.
    last_value = object()
    for value in l:
        if value == last_value:
            i += 1
        else:
            i = 0
            last_value = value
        yield i, value

def init(roster_file_path, line_to_survey_info, correct_title=lambda x: x):
    '''
    This function is supposed to take in the title->survey mapping and
    clean up the titles to reference classes.
    '''

    '''
    An example of the gdocs formula used to name the surveys was:

    =CONCATENATE(IF(EQ(K2,""), "", CONCATENATE(K2, "/")), A2, " ",B2,
     ": ",D2, " - DEN HKN Survey Spring 2013")

    column A: subject (ECE)
    column B: course number
    column C: section (when applicable - i.e. ECE 198 JL/KL)
    column D: course title
    column F: generated survey title
    column K: crosslisted names - usually there was only one, e.g. "MATH 362",
        but the most extreme example was "CS 450, CSE 401, MATH 450"
        (for ECE 491).

    Worth noting: I thought that ECE 198JL/KL would have both been special
    cases.  While they did get separate surveys, the JL/KL doesn't show up
    in the survey names (though they can be differentiated by the course
    titles).

    One more caveat though: the current implementation of survey-scripts
    puts these titles in the file names.  This means that it has to squash
    certain special characters.  At the time of the data download, this was:
    /, \, ., got changed to _
    : got changed to -

    But one more thing: the download script could only grab the portion of
    the title that was displayed - part was hidden, replaced by "...".
    Hence the titles end in underscores, complicating the logic we need.

    With all this in mind, we can now construct this function.  While it
    would be possible to do it all without the original data, knowing
    semester-specific schema, this seems error-prone and less reusable.
    '''

    survey_info_by_title = dict()
    with open(roster_file_path, 'r') as roster:
        lines = [line for line in csv.reader(roster)]

    for line in lines[1:]:

        survey_title, survey_info = line_to_survey_info(line)

        # file_title is a slight lie because of spring2013_correction -
        # the end of the file name is stripped because webtools decided
        # it was too long and it should convert part of it to ... instead.
        # Without figuring out their exact algorithm, chopping it off early
        # is best.
        file_title = title_to_filename_chars(
                correct_title(survey_title)
            )

        survey_info_by_title[file_title] = survey_info

    def attach_survey_info(title, survey):
        corrected_title = correct_title(title) 
        survey.set_info(**survey_info_by_title[corrected_title])

    return attach_survey_info

def title_to_filename_chars(title):

    # I can't find a reason for needing this, but mysteriously, though CS 450
    # is listed with ,'s in the roster, it is titled with exclusively /s.  So
    # this is completely a hack
    title = title.replace(', ', '/')

    # all the ugly replacements because the titles are shoved into filenames
    return (title.replace('/', '_').replace('\\', '_')
            .replace('.', '_').replace(':', '-'))

def spring2013_correction(input):
    '''strips of the " - DEN HKN" and everything after it.
       This solves the ... problem'''

    return input.rsplit(' - DEN HKN')[0]

def minusA(letter):
    return ord(letter) - ord('A')


def sp13_line_to_survey_info(line):
    # read the proper columns
    subject = line[minusA('A')]
    course_number = line[minusA('B')]
    section = line[minusA('C')]
    course_title = line[minusA('D')]
    survey_title = line[minusA('F')]

    survey_info = dict(
        # concatenates subject and number, i.e. "ECE" and "385"
        course_name  = subject + " " + course_number,
        course_title = course_title,
        crosslist    = [alt_name.strip() for alt_name in line[minusA('K')].split(',')],
    )

    if section:
        survey_info['section'] = section

    return survey_title, survey_info

def fa12_line_to_survey_info(line):
    # read the proper columns
    subject = line[minusA('D')]
    course_number = line[minusA('E')]
    course_name = subject + ' ' + course_number

    course_title = line[minusA('G')]
    raw_crosslist = line[minusA('F')]

    # had to rename some files to make this work (some were - HKN DEN Survey)
    survey_title = raw_crosslist + ' - DEN HKN Survey'
    crosslist = [ alt_name for alt_name in raw_crosslist.split('/') if alt_name != course_name ]

    return survey_title, dict(
        course_name = course_name,
        course_title = course_title,
        crosslist = crosslist,
    )

attach_survey_info_sp13 = init(
    "rosters/Spring 2013 Surveys.csv",
    sp13_line_to_survey_info,
    correct_title=spring2013_correction,
)
attach_survey_info_fa12 = init(
    "rosters/Fall 2012 Survey Contacts.csv",
    fa12_line_to_survey_info,
)
