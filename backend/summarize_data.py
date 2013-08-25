from collections import Counter

def summarize(surveys):
    
    # this excludes surveys with no responses.
    return dict(
        ((survey._course_name, summarize_one(survey))
         for survey in surveys if survey.has_answers())
    )

def summarize_one(survey):
    summary=[]
    for q in survey.questions:
        question_summary = dict()
        question_summary['prompt'] = q.question_text
        if q.options: # this covers single-choice and multi-choice
            # TODO: output options that weren't chosen.

            counts = Counter(ans for r_num, ans, other in q.answers)
            question_summary['answers'] = [
                (opt, counts[opt]) for opt in q.options
            ]

            if q.other_is_enabled():
                question_summary['others'] = [
                    other for r_num, ans, other in q.answers if other
                ]
        else: # this covers freeform questions
            question_summary['answers'] = [
                ans for r_num, ans, other in q.answers if ans
            ]
        summary.append(question_summary)

    return summary
