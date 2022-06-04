#!/usr/bin/env python


from multiprocessing.dummy import current_process
import os, sys, re
import operator
import argparse
import hashlib
import operator

DEBUG = False

vid_exts = [
    '.avi',
    '.mp4',
    '.mpeg',
    '.mpg',
    '.flv',
    '.mov',
]

img_exts = [
    '.jpg',
    '.png',
    '.jpeg',
    '.gif',
    '.zip',
    '.pdf',
]

dupe_indicator = '!'
max_marks = 14


ap = argparse.ArgumentParser()
ap.add_argument('-t','--type', required=False, help='img or vid, img is default')
ap.add_argument('-r','--recursive', action='store_true', default=False, help='recursive')
ap.add_argument('--rename-delete', action='store_true', default=False, help='action type')
ap.add_argument('-s','--simulate', action='store_true', default=False, help='simulate')
ap.add_argument('-z','--track-size', action='store_true', default=False, help='track size of deletions')
ap.add_argument('target', help='directory to search')
args = ap.parse_args()
total_size_deleted = 0

if args.type == 'img':
    exts = img_exts
elif args.type == 'vid':
    exts = vid_exts
else:
    print("--type must be either 'img' or 'vid'!")
    sys.exit()




def md5sum(file):
    md5 = hashlib.md5()
    with open(file,'rb') as f:
        for chunk in iter(lambda: f.read(128*md5.block_size),b''):
            md5.update(chunk)
    return md5.hexdigest()


# make a generator for all file paths within dirpath
basedir = os.getcwd()
dirpath = os.path.abspath(args.target)
search_root = os.path.join(basedir, dirpath)

print("searching {} for dupes of type {}".format(search_root, ', '.join(exts)))


if args.recursive:
    print("recursive....")
else:
    print("NOT recursive....")
all_files = ( os.path.join(basedir, filename) for basedir, dirs, files  \
    in os.walk(search_root) for filename in files \
        if args.recursive or basedir == search_root  )

files_and_sizes = ( (path, os.path.getsize(path)) for path in all_files \
    if path.lower().endswith(tuple(exts)) )

sorted_tuples = sorted( files_and_sizes, key = operator.itemgetter(1), reverse=True )
print("found {} potential files".format(len(sorted_tuples)))







matches = {}

def count_marks(fn):
    # TODO:  probably need special regex handling below for special characters....
    m = max( [len(x) for x in re.findall(r'['+dupe_indicator+']+', fn)] , default=0)
    return m
    # let's handle mark reduction elsewhere
    #return 0 if m < 2 else m

# def choose_filename(h):
#     # sort by length, remove basedir
#     fns = sorted( sorted([ os.path.split(fn)[1] for fn in  matches[h] ]) , key=len)
#     basedir,_ = os.path.split(matches[h][0])
#     basename , ext = os.path.splitext(fns[0])
#     bestname = basename.strip()
#     # print("starting basename = {}".format(basename))
#     # print("starting bestname = {}".format(bestname))
#     # print(fns)

#     marks = count_marks(bestname)

#     # for longer names
#     for n in fns[1:]:
#         fpart, ext = os.path.splitext(n)
#         # print("fpart = {}".format(fpart))
#         delta = fpart.replace(basename, '').strip()
#         # count marks
#         marks = max(marks, count_marks(delta))
#         # remove junk
#         delta = re.sub(r'[\W\S]+',' ', delta).strip()
#         if re.match(r'\s*$', delta):
#             continue


#         # print("clean delta = {}".format(delta))
#         #if re.search(r'copy\d?', delta, re.I):
#         if re.match(r'^copy\s*\d?$', delta, re.I):
#             continue
#         if re.match(r'^\d+$', delta):
#             continue
#         else:
#             bestname = ' '.join([bestname, delta])

#     return (os.path.join(basedir, bestname+ext), marks)

# def clean_fpart_name(n):
#     # remove marks from delta
#     n = n.replace(dupe_indicator, '')
#     # remove non alpha non space junk
#     n = re.sub(r'[^\w\s]+',' ', n)
#     if re.match(r'^\s*$', n):
#         return ''
#     # eliminate dupe conventions
#     n = re.sub(r'copy','', n, re.I) 
#     # this is broke,but try to kill single/double digits at the end
#     n = re.sub(r'\s+-?\d+\s+', ' ', n)
#     # consolidate spaces
#     n = re.sub(r'\s+',' ', n)
#     n = n.strip()
#     return n



def most_common_long_prefix(fns):
    """ operates on fparts only"""

    if len(fns) == 1:
        return fns[0]
    prefixes = {}
    for fn in fns:
        prefix = None
        for t in fn.split():
            if re.match(r'copy', t, re.I):
                continue
            t = re.sub(r'-\d\d?$','',t)
            if not t:
                continue
            if re.match(r'^\d\d?$', t):
                continue

            new_prefix = ' '.join([prefix, t]) if prefix else t
            if new_prefix in prefixes:
                prefixes[new_prefix] += 1
            else:
                prefixes[new_prefix] = 1
            prefix = new_prefix

    mv = max(prefixes.values())
    mclp = [ key for key in prefixes.keys() if prefixes[key] == mv ] 
    if mv > 1:
        mclp.sort(key=len, reverse=True)
    else:
        mclp.sort(key=len, reverse=False)

    return mclp[0]


"""

## TODO:

# this is a pretty broken attempt....
def longest_common_prefix(fns):
    if not fns:
        return ''
    elif len(fns) == 1:
        return fns[0]

    arr = fns.sort()
    result = ""
    # Compare the first and the last string character
    # by character.
    for i in range(len(arr[0])):
        #  If the characters match, append the character to
        #  the result.
        if arr[0][i] == arr[-1][i]:
            result += arr[0][i]
        # Else, stop the comparison
        else:
            break
    return result.strip()


# need to find not longest common prefix, but rather most common long prefix...

# consider

# foobar
# long_prefix_with_stuff here
# long_prefix_with_stuff here 1
# long_prefix_with_stuff here 2
# long_prefix_with_stuff here 3
# zeds dead baby

# maybe...
# find longest common prefix over whole list
# if zero, remove top or bottom...

# or 

# dictionary
# for each string
    # for each token
        # add string up to and including token to dictionary or increment count if exists
# take key with highest value count, break ties with longest

"""




def choose_starting_name(fns):
    """ currently using only basedir from here...."""
    if len(fns) == 1:
        return fns[0]
    
    rootiest_dir = ''
    longest_fpart = ''
    final_ext = ''
    for f in fns:
        dir, fn = os.path.split(f)
        fpart, ext = os.path.splitext(fn)
        if len(dir) < len(rootiest_dir):
            # replace only if none selected or candidate is alphabetically less than
            if not rootiest_dir or dir < rootiest_dir:
                rootiest_dir = dir

        if len(fpart) > len(longest_fpart):
            longest_fpart = fpart
            final_ext = ext
    return (rootiest_dir, longest_fpart, final_ext)








def choose_filename_new(h):

    fns = [f for f in matches[h]]
    (final_basedir, _, final_ext) = choose_starting_name(fns)


    # separate out paths, fparts and exts
    fparts = [os.path.splitext(os.path.split(x)[1])[0] for x in fns]

    #bestname = basename = most_common_long_prefix( [os.path.splitext(x)[0] for x in fns ])
    bestname = basename = most_common_long_prefix(fparts)
    marks = count_marks(basename)
    # print("\t\tstarting basename = {}".format(basename))
    # print("starting bestname = {}".format(bestname))
    # print(fns)

    for fpart in fparts:
        #print("base fpart = #{}#".format(fpart))
        delta = fpart.replace(basename, '').strip()
        #print(f'starting delta = #{delta}#')
        # count marks
        marks = max(marks, count_marks(delta))
        # remove marks from delta
        delta = delta.replace(dupe_indicator, '')
        # remove non alpha non space junk
        delta = re.sub(r'[^\w\s\-]+',' ', delta)
        delta = re.sub(r'\s+',' ', delta)
        delta = delta.strip()
        #print(f'clean delta before tokenizing = #{delta}#')
        if re.match(r'^-?\d\d?$',delta):
            continue
        if not delta or re.match(r'\s*$', delta):
            continue

        # TODO:  reduce code duplication here
        for t in delta.split():
            #print(f'delta = #{delta}#')
            #print(f'token = #{t}#')
            t = t.strip()
            if t in bestname:
                continue
            t = re.sub(r'-?\d\d?$','',t)
            if t in bestname:
                continue
            if re.match(r'^copy$',t, re.I):
                continue
            if t:
                #print(f'\t\t adding token {t} to bestname')
                bestname = ' '.join([bestname, t])

    # don't max out the 255 char filename max length
    fn_len = 253 - max_marks
    return (os.path.join(final_basedir, ''.join([bestname[:fn_len], final_ext])), marks)


def add_marks_to_name(n, h, carryover_marks):
    bn , ext = os.path.splitext(n)
    # consider whether to add or max?
    # l = max([ len([dupe_indicator for x in matches[h]]) - 1 , carryover_marks])
    # l =  len([dupe_indicator for x in matches[h]]) - 1 + carryover_marks
    current_marks = len(matches[h]) -1  # this should always be >=2 

    if args.type == 'img':
        #l =  len([dupe_indicator for x in matches[h]]) - 1 + carryover_marks
        l = current_marks + carryover_marks
    else:
        #l = max([ len([dupe_indicator for x in matches[h]]) - 1 , carryover_marks])
        l = max([current_marks, carryover_marks])

    if l > max_marks:
        return ''.join([
            bn, 
            ' ',
            dupe_indicator,
            dupe_indicator,
            str(l),
            dupe_indicator,
            dupe_indicator,
            ext,
        ])
    if l > 0:
        return bn + ' ' + ''.join([dupe_indicator for x in range(l)]) + ext
    else:
        return bn + ext





def match_action(h):
    global total_size_deleted
    print("match action")
    if args.rename_delete:
        (newname, carryover_marks) = choose_filename_new(h)
        newname = add_marks_to_name(newname, h, carryover_marks)
        try:
            print("\t Move: {} to {} ".format(matches[h][0], newname))
            if not args.simulate:
                os.replace(matches[h][0], newname)
            for x in matches[h][1:]:
                print("\t rm:   {} ".format(x))
                if args.track_size:
                    total_size_deleted += os.path.getsize(x)
                if not args.simulate:
                    os.remove(x)
        except Exception as e:
            print(e)
            sys.exit()
        matches.pop(h)
            



def handle_match_set(pd_set):
    # same hash should never have a different file size
    # so when this gets called, we are pretty damn sure we have all fns for a given hash
    hashes = set()
    for (fn,hash) in pd_set:
        if hash not in matches:
            matches[hash] = []
        if fn not in matches[hash]:
            matches[hash].append(fn)
        hashes.add(hash)
    for h in hashes:
        if len(matches[h]) > 1:
            match_action(h)





possible_dupe_set = []
prev_size = 0
for fn, fsize in sorted_tuples:

    #print("\tconsidering {}".format(fn) )
    #print("\tcurrent size = {}\t prev_size = {}".format(fsize, prev_size) )

    if prev_size == fsize: 
        # if fn is a likely dupe of previous
        possible_dupe_set.append( (fn, md5sum(fn)) )
    else:
        # if fn is start of a new run....
        handle_match_set(possible_dupe_set)
        possible_dupe_set = [ (fn, md5sum(fn)) ]

    prev_size = fsize



def convert_size(size_bytes):
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

if args.track_size:
    #print("total space saved = {}".format(hurry.filesize.size(total_size_deleted)))
    print("total space saved = {}".format(convert_size(total_size_deleted)))