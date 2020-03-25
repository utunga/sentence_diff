from sentence_diff import SentenceDiff
import csv


def process_row(row, writer):
    actual_sentence = row['transcript']
    target_sentence = row['target']

    if len(actual_sentence.strip()) == 0:
        return
    if len(target_sentence.strip()) == 0:
        return

    print("{}-{}".format(actual_sentence, target_sentence))

    diff = SentenceDiff(actual_sentence, target_sentence)
    row['wer'] = diff.wer()
    row['score'] = diff.chatterize_score() * 100
    writer.writerow(row)


with open('pivotable.csv', encoding='utf-8') as csv_file_in:
    with open('pivotable_out.csv', 'w', newline='', encoding='utf-8') as csv_file_out:
        reader = csv.DictReader(csv_file_in)
        first_row = reader.__next__()
        field_names = list(first_row.keys())
        field_names.append('score')
        writer = csv.DictWriter(csv_file_out, fieldnames=field_names,
                                delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        process_row(first_row, writer)

        for row in reader:
            process_row(row, writer)

