import os, sys, re, stat
from optparse import OptionParser
from datetime import datetime

ret_code = '\n'

class Processor(object):
    def metric(self, f):
        code = open(f).read()
        code_no_comment = self.remove_comment(code)
        # print code_no_comment
        return dict([('loc', len(code.split(ret_code))),
                     ('loc_no_comment', len(code_no_comment.split(ret_code)))] + 
                    [(k, len(re.findall(r'\b%s\b' % k, code_no_comment))) for k in self.keywords])
    def remove_comment(self, code):
        s = re.sub(r'%s(?:.|%s)*?%s' % (re.escape(self.comment_region_start), ret_code, re.escape(self.comment_region_end)),
                   r'', code, flags=re.M)
        if self.comment_line:
            s = re.sub(r'^\s*%s.*%s' % (re.escape(self.comment_line), ret_code), r'', s, flags=re.M)
            s = re.sub(r'%s.*' % re.escape(self.comment_line), r'', s)
        return s

class Java(Processor):
    """Processor class for Java"""
    language = 'JAVA'
    keywords = ['if', 'else', 'try', 'catch', 'finally']
    comment_region_start = '/*'
    comment_region_end   = '/*'
    comment_line         = '//'

class CPP(Processor):
    """Processor class for C++"""
    language = 'C++'
    keywords = ['if', 'else', 'try', 'catch']
    comment_region_start = '/*'
    comment_region_end   = '/*'
    comment_line         = '//'

class C(Processor):
    """Processor class for C"""
    language = 'C'
    keywords = ['if', 'else']
    comment_region_start = '/*'
    comment_region_end   = '/*'
    comment_line         = None

def main(processors):
    try:
        parser = OptionParser("usage: %prog [options] dir")
        parser.add_option("-o", "--out", dest="out",
                          help="write report to FILE", metavar="FILE")
        (options, args) = parser.parse_args()
        target_dir = args[0]
        if options.out:
            out = open(options.out, 'w')
        else:
            out = sys.stdout 
        data = []
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for path in [os.path.join(root, f) for f in files]:
                ext = os.path.splitext(path)[1]
                if not ext in processors:
                    continue
                processor = processors[ext]
                d = processor.metric(path)
                d['path']     = path
                d['language'] = processor.language
                mod_dt = datetime.fromtimestamp(os.stat(path).st_mtime)
                d['mod_date'] = mod_dt.date()
                d['mod_time'] = mod_dt.time()
                data.append(d)

        colnames = ['loc', 'loc_no_comment'] + list(reduce(set.union, [set(x.keywords) for x in processors.values()]))
        keys = ['path', 'language', 'mod_date', 'mod_time'] + colnames
        out.writelines(','.join(keys) + ret_code)
        for d in data:
            out.write(','.join([str(d.get(k, 0)) for k in keys]) + ret_code)
    except Exception, e:
        sys.stderr.write(str(e) + ret_code)


if __name__ == '__main__':
    main({ ".java" : Java(),
           ".cpp" : CPP(),
           ".cc" : CPP(),
           ".c" : C()})
