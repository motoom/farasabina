import glob       
import os
import datetime
import collections
from pprint import pprint as pp
import csv


months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


# Output files
pre = csv.writer(open("pre.csv","wb"))
post = csv.writer(open("post.csv","wb"))
both = csv.writer(open("both.csv","wb"))
             
fields = ("participant", "congruent", "targetcolor", "trial", "responsetime", "correct")
pre.writerow(fields)
post.writerow(fields)
both.writerow(fields)


def safecolname(name):
    """ Given a CSV column name, return a name safe for use as an attribute name. 
        Guards against dots in column names, and empty column names. """
    name = name.strip()
    if not name:
        name = "empty_"
    name = name.replace(".", "_")
    return name
        
         
def saferow(row):
    """ Return a copy of the dict 'row' such that all keys can safely be used
        as attribute names. """
    d = {}
    for key, val in row.iteritems():
        safekey = safecolname(key)
        d[safekey] = val
    return d


def process(participant, fn, output, trial):
    print "Processing", fn, participant, trial

    # Some CSV files use ',' as a delimiter, some use ';'.
    firstline = open(fn, "rbU").readline()
    delimiter = csv.Sniffer().sniff(firstline).delimiter
    
    rs = csv.DictReader(open(fn, "rbU"), delimiter=delimiter)
    safefieldnames = [safecolname(fieldname) for fieldname in rs.fieldnames]
    Row = collections.namedtuple("Row", safefieldnames)
    for r in rs:
        output.writerow((participant, r["congruent"], r["letterColor"], trial, r["resp.rt"], r["resp.corr"]))
        r = saferow(r)
        item = Row(**r)


def inputfiles():
    """ See what files we got, and extract the metadata from the filenames.
        Return a dict containing all the information, keyed on participant number. """
    d = collections.defaultdict(list) # Mapping from participant number => [(pre-date, pre-filename), (post-date, post-filename)]
    for fn in glob.glob("*.csv"):
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
for participant, datafiles in participants.iteritems():
    if len(datafiles) != 2:
        raise Exception("Participant %d has %d data files, should be exactly 2." % (participant, len(datafiles)))
    datafiles.sort()

# Process the datafiles of each participant.
for participant, datafiles in participants.iteritems():
    print "Participant", participant
    prefn, postfn = [filename for date, filename in datafiles]
    process(participant, prefn, pre, "pre")
    process(participant, postfn, post, "post")
