import glob
import os
import datetime
import collections
import csv
import codecs

# Output files
fields = ("participant", "congruent", "targetcolor", "trial", "responsetime", "correct")
pre = csv.writer(codecs.open("pre.csv", "wb", "utf8"))
pre.writerow(fields)
post = csv.writer(codecs.open("post.csv", "wb", "utf8"))
post.writerow(fields)


def checkresponse(correct, given):
    if given == "return":
        given = "enter"
    return int(correct == given)


def process(participant, fn, output, part):
    print("Processing %s %d %s" % (fn, participant, part))

    # Some CSV files use ',' as a delimiter, some use ';'.
    firstline = codecs.open(fn, "rbU", "utf8").readline()
    delimiter = csv.Sniffer().sniff(firstline).delimiter

    rs = csv.DictReader(codecs.open(fn, "rbU", "utf8"), delimiter=delimiter)
    for r in rs:
        correct = r["corrAns"]
        given = r["resp.keys"]
        is_correct = checkresponse(correct, given)
        if given == "None":
            rt = -1
        else:
            rt = int(1000 * float(r["resp.rt"]))
        output.writerow((participant, r["congruent"], r["letterColor"], correct, given, part, rt, is_correct))


def inputfiles():
    """ See what files we have to process, and extract the metadata from the filenames.
        Return a dict containing all the information, keyed on participant number. """
    rs = csv.reader(codecs.open("allfilenames.csv", "rbU", "utf8"), delimiter=",")
    fns = [r[2] for r in rs]
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    d = collections.defaultdict(list) # Mapping from participant number => [(pre-date, pre-filename), (post-date, post-filename)]
    for fn in fns:
        if not os.path.exists(fn):
            raise Exception("Input file '%s' is mentioned in 'allfilenames.csv', but not found" % fn)
        basename, ext = os.path.splitext(fn)
        parts = basename.split("_")
        if len(parts) != 5:
            continue
        participant, year, monthname, day, _ = parts
        month = months[monthname.lower()]
        date = datetime.date(int(year), month, int(day))
        participant = int(participant)
        d[participant].append((date, fn))
    return d


participants = inputfiles()

# Make sure every participant has exactly two data files, sort the datafiles chronologically.
for participant, datafiles in participants.items():
    if len(datafiles) != 2:
        raise Exception("Participant %d has %d data files, should be exactly 2." % (participant, len(datafiles)))
    datafiles.sort()

# Process the datafiles of each participant.
for participant, datafiles in participants.items():
    print("\nParticipant %d" % participant)
    prefn, postfn = [filename for date, filename in datafiles]
    process(participant, prefn, pre, "pre")
    process(participant, postfn, post, "post")
