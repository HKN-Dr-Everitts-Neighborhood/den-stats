from collections import Counter
from random import shuffle

# This module reads Survey objects (survey_obj.py) and outputs the summarized json
# that the frontend uses to draw the graphs.

def summarize(surveys):
    
    # this excludes surveys with no responses.
    return dict(
        ((survey._course_name + ' - ' + survey._course_title, summarize_one(survey))
         for survey in surveys if survey.has_answers())
    )

def summarize_one(survey):
    summary=[]
    for q in survey.questions:
        question_summary = dict()
        question_summary['prompt'] = q.question_text
        question_summary['type'] = q.type
        if q.options: # this covers single-choice and multi-choice
            # TODO: output options that weren't chosen.

            counts = Counter(ans for r_num, ans, other in q.answers)
            question_summary['answers'] = [
                (opt, counts[opt]) for opt in q.options
            ]

            if q.other_is_enabled():
                others = [
                    other for r_num, ans, other in q.answers if other
                ]
                # shuffle for anonymization
                shuffle(others)
                question_summary['others'] = others
        else: # this covers freeform questions
            answers = [ ans for r_num, ans, other in q.answers if ans ]
            # shuffle for anonymization
            shuffle(answers)
            question_summary['answers'] = answers

        summary.append(question_summary)

    return summary
