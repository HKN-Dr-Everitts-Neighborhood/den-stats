#! python

import csv, json, sys, os.path
from unidecode import unidecode

def comments_to_csv(filename):
    with open(filename) as file:
        semester_data = json.load(file)

    out_filename = filename.rsplit('.', 1)[0] + '.csv'
    print "writing to", out_filename
    with open(out_filename, 'wb') as output_file:
        # default line terminator is \r\n, unfortunately.
        csv_out = csv.writer(output_file, lineterminator='\n')
        csv_out.writerow(['class', 'question', 'answer', 'include? (y/n)'])
        # semester_data is a map from class_name to a list of questions
        # in the survey given to that class
        for class_name, survey_data in semester_data.iteritems():
            for question in survey_data:
                # we're only interested in freeform questions - no need to curate
                # single-choice / multi-choice answers
                if question['type'] == "freeform":
                    for answer in question['answers']:
                        # csv writer can't handle unicode.
                        csv_out.writerow([class_name, question['prompt'],
                                          unidecode(answer), ''])

def annotated_csv_and_json_to_new_json(json_filename, csv_filename):
    with open(json_filename, 'rb') as json_file:
        json_data = json.load(json_file)
    with open(csv_filename, 'rb') as csv_file:
        csv_data = [ row for row in csv.reader(csv_file) ]

    # reorganize csv_data into something more useful.
    # NOTE: it turns out that google docs (or csv reader/writer... not totally
    # sure) sometimes removes trailing whitespace from fields (particularly,
    # from answer)
    yn_by_class_q_and_answer = dict(
        ((class_name, question, answer.strip()), yn) for
            class_name, question, answer, yn in csv_data
    )

    for class_name, survey_data in json_data.iteritems():
        for question in survey_data:
            if question['type'] == "freeform":
                new_answers = []
                for answer in question['answers']:
                    # it turns out that some of the answers have \r\n in them, but setting
                    # lineterminator to \n when writing the csv doesn't preserve that.
                    # also must unidecode here since comments_to_csv does it.
                    sanitized_answer = unidecode(answer.replace('\r\n', '\n').strip())
                    yn = yn_by_class_q_and_answer[
                        (class_name, question['prompt'], sanitized_answer)]
                    assert yn in ('y', 'n'), "invalid y/n value: %s" % yn
                    if yn == 'y':
                        new_answers.append(answer)
                question['answers'] = new_answers

    output_filename = os.path.join("filtered_data", os.path.basename(json_filename))
    with open(output_filename, 'w') as output_file:
        json.dump(json_data, output_file)

def main():
    if len(sys.argv) == 3 and sys.argv[1] == "make_csv":
        comments_to_csv(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "make_new_json":
        annotated_csv_and_json_to_new_json(sys.argv[2], sys.argv[3])
    else:
        usage()

def usage():
    print "Usage:"
    print "python", sys.argv[0], "make_csv", "<semester's json>" 
    print "python", sys.argv[0], "make_new_json", "<semester's json> <annotated csv>"

if __name__ == "__main__":
    main()
