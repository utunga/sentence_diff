from sentence_diff import WordDiff
import csv

with open('keyword_diffs.csv', newline='', encoding="utf-8") as csv_file_in:
    with open('keyword_diffs_out.csv', 'w', newline='', encoding="utf-8") as csv_file_out:
        writer = csv.writer(csv_file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["target_text","recognized_text","confidence_score","audio_mp3_file", "similarity", "pass_fail"])
        reader = csv.reader(csv_file_in, delimiter=',', quotechar='"')
        reader.__next__()
        for row in reader:
            actual = row[0]
            target = row[1]
            confidence = float(row[2])

            if len(actual.strip()) == 0:
                continue
            if len(target.strip()) == 0:
                continue

            print("{}-{}".format(actual, target))

            diff = WordDiff(actual, target)
            pass_fail, similarity = diff.chatterize_score()
            row.append(similarity * 100)
            row.append(pass_fail)
            writer.writerow(row)
