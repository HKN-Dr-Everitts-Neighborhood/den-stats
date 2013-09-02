
Other = "other"
QuestionTypes = set([
    "undetermined",
    "single-choice",
    "multi-choice",
    "freeform",
])

class Question(object):
    '''There are several different types of supported questions.
    For ease of use, this class encompasses them all, and allows the
    type of question to be set after instantiation.'''

    def __init__(self):
        self.question_text = None
        self.other_enabled = False
        self.answers = []
        self.type = "undetermined"
        self.options = None
    
    def set_text(self, question_text):
        self.question_text = question_text

    def set_type(self, type):
        assert self.type == "undetermined"
        assert type in QuestionTypes
        assert type == "freeform" or (type != "freeform" and self.options)
        self.type = type

    def enable_other(self):
        self.other_enabled = True

    def other_is_enabled(self):
        return self.other_enabled

    def set_options(self, options):
        assert self.type != "freeform"
        assert isinstance(options, list)
        self.options = options

    def add_answer(self, response_num, answer, other=None):
        self._assert_valid_answer_type(answer, other)
        # worth noting: multi-choice questions can get
        # many entries in answers per responder.
        self.answers.append((response_num, answer, other))

    def _assert_valid_answer_type(self, answer, other):
        assert self.type != "undetermined"
        assert self.other_enabled or not other
        if self.type in ("single-choice", "multi-choice"):
            assert answer in self.options
        elif self.type == "freeform":
            assert isinstance(answer, basestring)

    def copy(self):
        ''' Note: this copies everything but the answers '''
        new_q = Question()
        new_q.set_text(self.question_text)
        if self.other_enabled:
            new_q.enable_other()
        if self.options:
            new_q.set_options(self.options)
        new_q.set_type(self.type)

        return new_q

class Survey(object):
    '''A Survey is a set of questions.  You can also add answers to a
    survey, but they get passed through to the corresponding question'''

    def __init__(self):
        self.questions = []
        self.num_answers = 0

    # Note: questions must be added in order!
    def add_question(self, q_obj):
        assert isinstance(q_obj, Question), "q_obj has the wrong type!"
        self.questions.append(q_obj)
        self.num_answers += len(q_obj.answers)

        return len(self.questions)-1

    def get_question(self, num):
        return self.questions[num]

    def add_answer(self, respondent_num, question_num, answer, other=None):
        self.num_answers += 1
        self.questions[question_num].add_answer(
            respondent_num,
            answer,
            other
        )

    def has_answers(self):
        return self.num_answers > 0

    def set_info(self, course_name, course_title=None, crosslist=None, section=None):
        '''
        Function to set meta-info about the class that the survey is for.

        @param course_name - subject and number, e.g. "ECE 385"
        @param course_title - title of the course, i.e. "Digital Systems
            Laboratory" or something like that.
        @param crosslist - a list of the other names the course masquerades
            as, such as MATH 362 for ECE 313.  If the course isn't crosslisted,
            give an empty list.
        @param section - section of the class, if the survey was only for
            a specific section.  This would be used for ECE 198 JL (and KL)
            so we'd have course_name="ECE 198" and section="JL"
        '''
        
        assert isinstance(course_name, basestring) and course_name
        if course_title is not None:
            assert isinstance(course_title, basestring) and course_title
        if crosslist is not None:
            assert isinstance(crosslist, list)
        if section is not None:
            assert isinstance(section, basestring) and section

        self._course_name = course_name
        self._course_title = course_title
        self._crosslist = crosslist
        self._section = section
