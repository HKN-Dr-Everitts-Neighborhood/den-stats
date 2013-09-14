#! python
import csv, os.path

from survey_obj import (
    Survey,
    Question,
    Other,
)

# This is only half-reasonable since most the questions are from the original template.
type_map = {
    "What is your Major?": "single-choice",
    "Timestamp?": None,
    "Sample Question 2?": None,
    "Did you find lecture helpful and relevant ?": None, # ECE 385
    "What is your class standing based on the number of credit hours you have?": "single-choice",
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture?": "single-choice",
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, MPs etc.) outside of lecture and discussion section?": "single-choice", # from ECE 190 survey
    "Rate your programming experience prior to taking this class.": "single-choice", # from ECE 190 survey
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture, not including lab?": "single-choice", # from ECE 210 survey
    "How many hours per week, on average, do you spend on work for the lab section outside of the assigned lab time?": "single-choice", # ECE 210, 342
    "Rate the lab on relevance and helpfulness in relation to the class material?": "single-choice", # ECE 210 and ECE 310
    "Did you take ECE 311, the lab portion?": "single-choice", # ECE 310
    "How difficult is this course compared to your other technical courses?": "single-choice",
    "Do you have any other comments about the course?": "freeform",
    "If any, what previous coursework helped prepare you from this course?": "freeform",
    "How many hours per week, on average, do you spend on work for this lab outside of assigned lab time?": "single-choice", # ECE 310
    "Have you taken a discrete math class such as Math 213 or CS 173?  If so, rate how useful this class was in preparing you for ECE 313.": "single-choice", # ECE 313
    "Did you take ECE 343, the lab portion?": "single-choice", # ECE 342
    "If so, rate the lab on relevance and helpfulness in relation to the class material?": "single-choice", # ECE 342
    "How many hours per week, on average, do you spend on work for this class (homework, lab assignments, etc) outside of lecture and the assigned lab time?": "single-choice", # ECE 385
    "Rate the lecture on relevance and helpfulness?": "single-choice", # ECE 385
    "How many hours per week, on average, do you spend on work for this class (homework, reading, MPs, etc.) outside of lecture and discussion section?": "single-choice",
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, MPs, etc.) outside of lecture?": "single-choice", # ECE 411
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture (not including lab)?": "single-choice", # ECE 444
    "How many hours per week, on average, do you spend on the lab (lab reports, quizzes, etc.) outside of the assigned lab period?": "single-choice", # ECE 444
}

options_map = {
    "What is your Major?": {
        '*': ["Electrical Engineering", "Computer Engineering", "Computer Science", Other],
        'ECE 110': ["Electrical Engineering", "Computer Engineering", "Computer Science", "Industrial Engineering", "General Engineering", Other], # This is a hack - Industrial / General were not choices in the original survey, but so many people wrote it in, I had to add it.
    },
    "What is your class standing based on the number of credit hours you have?": ["Freshman", "Sophomore", "Junior", "Senior", Other],
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture?": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, MPs etc.) outside of lecture and discussion section?": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"], # ECE 190
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture, not including lab?": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"], # ECE 210
    "How many hours per week, on average, do you spend on work for the lab section outside of the assigned lab time?":  {
        "ECE 210": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
        "ECE 342": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours", "N/A"],
    },
    "Rate the lab on relevance and helpfulness in relation to the class material?": {
        "ECE 210": ['1 - Not helpful or relevant at all', '2','3','4','5 - Very helpful and relevant'],
        "ECE 310": ['1 - Not helpful or relevant at all', '2','3','4','5 - very helpful and relevant', 'N/A'],
    },
    "Did you take ECE 311, the lab portion?": ["yes", "no"], # ECE 310
    "How many hours per week, on average, do you spend on work for this lab outside of assigned lab time?": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours", "N/A"], # ECE 310
    "How difficult is this course compared to your other technical courses?": ["1 - Very easy", "2", "3", "4", "5 - Very difficult"],
    "Rate your programming experience prior to taking this class.": ["1 -  no programming experience", "2 - some programming experience", "3 - significant programming experience"],
    "Have you taken a discrete math class such as Math 213 or CS 173?  If so, rate how useful this class was in preparing you for ECE 313.": ["N/A - have not taken a discrete math class", "1 - Not very useful", "2", "3", "4", "5 - Very helpful"], # ECE 313
    "Did you take ECE 343, the lab portion?": ["yes", "no"], # ECE 342
    "If so, rate the lab on relevance and helpfulness in relation to the class material?":  {
        "ECE 342": ['1 - Not helpful or relevant at all', '2','3','4','5 - Very helpful and relevant'],
    },
    "How many hours per week, on average, do you spend on work for this class (homework, lab assignments, etc) outside of lecture and the assigned lab time?": {
        "ECE 385": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    },
    "Rate the lecture on relevance and helpfulness?": {
        "ECE 385": ['1 - Not relevant or helpful at all', '2','3','4','5 - very helpful and relevant'],
    },
    "How many hours per week, on average, do you spend on work for this class (homework, reading, MPs, etc.) outside of lecture and discussion section?": {
        "ECE 391": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    },
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, MPs, etc.) outside of lecture?": {
        "ECE 411": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    },
    "How many hours per week, on average, do you spend on work for this class (homework, reading, studying, etc.) outside of lecture (not including lab)?": {
        "ECE 444": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    },
    "How many hours per week, on average, do you spend on the lab (lab reports, quizzes, etc.) outside of the assigned lab period?" : {
        "ECE 444": ["0-3 hours", "4-7 hours", "8-11 hours", "12-15 hours", "16-19 hours", "20+ hours"],
    },
}

other_set = {
    "What is your Major?",
    "What is your class standing based on the number of credit hours you have?",
}

def google_docs_parser(folder, files):
    '''
    Returns a list of Survey objects.

    Note: this function is made for the Spring 2012 surveys.  There
    isn't an easy way to extract the surveys from Google Docs, so
    we only have the questions and responses - the possible choices
    are not in our dataset.
    '''
    
    surveys = []
    for f in files:
        if f.endswith('.csv') and '-' in f:
            print "Processing", f
            class_name = f.split('-')[1].strip().split('.')[0]

            with open(os.path.join(folder, f)) as csv_file:
                lines = [line for line in csv.reader(csv_file)]

            header = lines[0]
            answers = lines[1:]
            lines = None
            
            survey = Survey()

            survey.set_info(
                course_name=class_name,
                #course_title= # Fuck.
                #crosslist= # fuck fuck fuck...
            )

            # Add all questions in order
            cols_to_qnum = dict()
            qnum = 0
            for i, question in enumerate(header):
                q = Question()

                # Some questions are missing the question mark.
                question = question + ('?' if not question.endswith('?') and not question.endswith('.') else '')
                q.set_text(question)

                type = type_map[question]
                # skip this question if type is None
                if type:
                    if type in ("single-choice", "multi-choice"):
                        opts = options_map[question]
                        if isinstance(opts, dict):
                            if class_name in opts:
                                opts = opts[class_name]
                            else:
                                opts = opts['*']
                        q.set_options(opts)
                        
                        if question in other_set:
                            q.enable_other()

                    q.set_type(type)

                    survey.add_question(q)
                    cols_to_qnum[i] = qnum
                    qnum += 1
                else:
                    cols_to_qnum[i] = None

            for resp_num, response in enumerate(answers):
                # iterate through a single row
                for col_num, answer in enumerate(response):
                    q_num = cols_to_qnum[col_num]

                    if q_num is not None:
                        question = survey.get_question(q_num)
                        q_type = question.type

                        if q_type in ("single-choice", "multi-choice"):
                            if answer in question.options:
                                survey.add_answer(resp_num, q_num, answer)
                            else:
                                survey.add_answer(resp_num, q_num, Other, other=answer)
                        else:
                            survey.add_answer(resp_num, q_num, answer)

            surveys.append(survey)

    return surveys
