from sentence_diff import SentenceDiff
import csv

with open('edit_score_highlights.csv', newline='') as csv_file_in:
    with open('edit_score__highlights_out.csv', 'w', newline='') as csv_file_out:
        writer = csv.writer(csv_file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Actual Text","Target Text","Score By Words","Score By Letters", "New Score", "Attn", "New Score 2"]) #"Updated Wer", "Wer Score"
        reader = csv.reader(csv_file_in, delimiter=',', quotechar='"')
        reader.__next__()
        for row in reader:
            actual_sentence = row[0]
            target_sentence = row[1]

            if len(actual_sentence.strip()) == 0:
                continue
            if len(target_sentence.strip()) == 0:
                continue

            print("{}-{}".format(actual_sentence, target_sentence))

            diff = SentenceDiff(actual_sentence, target_sentence)
            row.append(diff.chatterize_score() * 100)
            writer.writerow(row)
