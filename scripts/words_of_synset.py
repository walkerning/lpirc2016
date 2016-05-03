# -*- coding: utf-8 -*-

import sys
import requests

base_url = "http://www.image-net.org/api/text/wordnet.synset.getwords?wnid="

def print_help():
    print "usage: python words_of_synset.py synset_file words_file [words_pkl]"

if len(sys.argv) not in {3, 4}:
    print_help()
    sys.exit(1)

if len(sys.argv) == 4:
    words_pkl = sys.argv[3]
else:
    words_pkl = None
synset_file = sys.argv[1]
words_file = sys.argv[2]

synset_word_dict = {}
with open(synset_file, "r") as sf:
    with open(words_file, "w") as wf:
        # index is 1-based, because class 0 is background class in many settings
        index = 1
        for l in sf.read().strip().split("\n"):
            wnid = l.strip()
            url = base_url + wnid

            r = requests.get(url)
            if r.status_code != requests.codes.ok:
                print >>sys.stderr, "%d for wnid %s: GET %s" % (r.status_code,
                                                                wnid,  url)
            else:
                pri_word = r.content.strip().split("\n", 1)[0]
                print "%d, %s: %s" % (index, wnid, pri_word)
                print >>wf, pri_word
                synset_word_dict[index] = pri_word

            index += 1

if words_pkl is not None:
    import cPickle
    with open(words_pkl, "w") as wf:
        cPickle.dump(synset_word_dict, wf)


