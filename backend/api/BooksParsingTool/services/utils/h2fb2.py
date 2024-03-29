from sgmllib import SGMLParser
import sys
import re
import tempfile
import os
import base64
import time
import mimetypes
import locale
import argparse

"""
HTML to FictionBook converter.

Usage: %prog [options] args
    -i, --input-file=FILENAME: (*.html|*.htm|*.html|*.*) Input file name, defaults to stdin if omitted.
    -o, --output-file=FILENAME: (*.fb2|*.*) Output file name, defaults to stdin if omitted.
    -f, --encoding-from=ENCODING_NAME:  Source encoding, autodetect if omitted.
    -t, --encoding-to=ENCODING_NAME DEFAULT=Windows-1251:    Result encoding(Windows-1251)
    -r,  --header-re=REGEX:         Regular expression for headers detection('')
    --not-convert-quotes:     Not convert quotes
    --not-convert-hyphen:     Not convert hyphen
    --skip-images:            Skip images, i.e. if specified do NOT include images. Default is to include images/pictures
    --not-convert-images:     Do not convert images to PNG, i.e. if specified keep images as original types. By default ALL in-line images are converted to PNG format.
    --skip-ext-links:         Skip external links
    --allow-empty-lines:      Allow generate tags <empty-line/>
    --not-detect-italic:      Not detect italc
    --not-detect-headers:     Not detect sections headers
    --not-detect-epigraphs:   Not detect epigraphs
    --not-detect-paragraphs:  Not detect paragraphs
    --not-detect-annot:       Not detect annotation
    --not-detect-verses:      Not detect verses
    --not-detect-notes:       Not detect notes
"""

"""
Chris TODO

    * output encoding, only really works if output is the same as system
      encoding. E.g. windows (command line) ascii, for most out-of-linux utf8
      this is due to use of str types contructed on the fly in the encoding
      specified in command line and then implict conversion from str to
      Unicode (joining str to Unicode type, needs explict decode)
    * uriparse  lib for proper URL parsing
    * images
        * check support for links to images (as well as alterative text display/processing)
        * handle images with url encoding, e.g. "my%20pic.jpg" versus "my pic.jpg" see url/uri above..
        * add a check "if image not (png or jpeg) convert to PNG"? Most readers seem to only support png and jpeg
    * check/change encoding of source to be (7 bit) ASCII, make this the default (instead if Windows-1252)
    * remove getopt, use: optparse, (my modified) wxoptparse or my document optparse
    * "em dash" only handles for html name tag "&mdash;",
        does not handle at all &#8212;
        and unicode/xml literal &#x2014; is displayed as text of that!
        probably due to use of SGML parser which isn't that flexible
    * test multi document html input
    * test href properly
    *   href bug if --not-convert-quotes  is not issued, get ">>" in href!!
    *   -i bug not working properly if file does not exist (uses stdin) - Low priority as file logic removed from class, html2fb does NOT suffer from this
    *   -o bug not working properly if file is in use, get no error/exception displayed and instead got to stdout - Low priority as file logic removed from class, html2fb does NOT suffer from this
        * TODO check python coding style/guide for open() versus file() -- http://mail.python.org/pipermail/python-dev/2004-July/045928.html
        * pep8 where appropriate (note use 120 cols not 80)
        * pychecker/pylint
        * process() open() has except without type, should have type and not ignore everything
        * convert_to_fb() out_file=file() also has except without type, should have type and not ignore everything
        * convert2png has try/except with no restrictions, errors are lost.
    * stuff before first header is book description: on/off
    * remove SGMLParser? replace with Beautiful Soup http://www.crummy.com/software/BeautifulSoup/
    * chardet suport - http://chardet.feedparser.org/
    * support of non ascii chracter (e.g. Unicode) like "...", mdash, etc. open/close quotes, check HaliReader on pocketPC (suspect missing unicode font) and import my mapping code
"""

version = '1.0.0'

# Module wide values
_SENTENCE_FIN = '\'".!?:\xBB\u2026'  # \xBB == >>, \u2026 == ...
_HEAD_CHARS = '0123456789VXILM*@'
_DIAL_START = '-\u2013\u2014'  # MINUS, N DASH, M DASH
_DIAL_START2 = ')-\u2013\u2014 .;'
_CH_REPL_AMP = '\x00'
_CH_REPL_LT = '\x01'
_CH_REPL_GT = '\x02'
_CH_LEFT_Q = '\\1\xab'
_CH_RIGHT_Q = '\xbb\\1'
_CH_FLOW = ' '
_CH_DOTS = '\u2026'
_CH_TIRE = '\u2013'
_RE_LQUOTES = re.compile('([ (;-])"')
_RE_RQUOTES = re.compile('"([ <&.,;?!)-])')
_RE_LQUOTES2 = re.compile('^((?:<[^>]*>)*)"', re.M)
_RE_RQUOTES2 = re.compile('"((?:<[^>]*>)*)$', re.M)
_RE_TAG = re.compile('<[^>]*>')
_RE_ROMAN = re.compile('^m?m?m?(c[md]|d?c{0,3})(x[lc]|l?x{0,3})(i[xv]|v?i{0,3})$', re.I)
_RE_EL = re.compile('<empty-line/>\s*(</section>)')
# Flags
_TAG_SKIP = 0x0001
_TAG_STARTP = 0x0002
_TAG_STRONG = 0x0004
_TAG_EM = 0x0008
_TAG_NOTSKIP = 0x0010
_TAG_ENDP = 0x0020
_TAG_PRE = 0x0040
_TAG_HEADER = 0x0080
_TAG_INP = 0x0100
_TAG_ID = 0x0200

_TAGS = {
    'a': _TAG_INP,
    'abbr': 0,
    'article': 0,
    'acronym': 0,
    'address': 0,
    'align': 0,
    'applet': 0,
    'area': 0,
    'b': _TAG_STRONG,
    'base': 0,
    'basefont': 0,
    'bdo': 0,
    'bgsound': 0,
    'big': 0,
    'blink': 0,
    'blockquote': 0,
    'body': 0,
    'br': _TAG_STARTP | _TAG_ENDP,
    'button': 0,
    'caption': 0,
    'center': 0,
    'cite': _TAG_EM | _TAG_ID,
    'code': 0,
    'col': 0,
    'colgroup': 0,
    'comment': 0,
    'dd': 0,
    'del': 0,
    'dfn': 0,
    'dir': 0,
    'div': 0,
    'dl': 0,
    'dt': 0,
    'em': _TAG_EM,
    'embed': 0,
    'fieldset': 0,
    'font': 0,
    'form': _TAG_SKIP,
    'frame': 0,
    'frameset': 0,
    'h0': _TAG_HEADER,
    'h1': _TAG_HEADER,
    'h2': _TAG_HEADER,
    'h3': _TAG_HEADER,
    'h4': _TAG_HEADER,
    'h5': _TAG_HEADER,
    'h6': _TAG_HEADER,
    'head': _TAG_SKIP,
    'hr': _TAG_ENDP,
    'html': 0,
    'i': _TAG_EM,
    'iframe': 0,
    'ilayer': 0,
    'img': _TAG_ENDP,
    'input': 0,
    'ins': 0,
    'isindex': 0,
    'kbd': 0,
    'keygen': 0,
    'label': 0,
    'layer': 0,
    'legend': 0,
    'li': 0,
    'link': 0,
    'listing': _TAG_PRE,
    'map': 0,
    'marquee': 0,
    'menu': 0,
    'meta': 0,
    'multicol': 0,
    'nextid': 0,
    'nobr': 0,
    'noembed': _TAG_SKIP,
    'noframes': _TAG_SKIP,
    'nolayer': 0,
    'nosave': 0,
    'noscript': _TAG_SKIP,
    'object': 0,
    'ol': 0,
    'optgroup': 0,
    'option': 0,
    'p': _TAG_STARTP | _TAG_ENDP,
    'param': 0,
    'plaintext': _TAG_PRE,
    'pre': 0,
    'q': 0,
    'rb': 0,
    'rbc': 0,
    'rp': 0,
    'rt': 0,
    'rtc': 0,
    'ruby': 0,
    's': 0,
    'samp': 0,
    'script': _TAG_SKIP,
    'select': 0,
    'server': 0,
    'servlet': 0,
    'small': 0,
    'spacer': 0,
    'span': 0,
    'strike': 0,
    'strong': _TAG_STRONG | _TAG_INP,
    'style': _TAG_SKIP,
    'sub': 0,
    'sup': 0,
    'table': 0,
    'tbody': 0,
    'td': 0,
    'textarea': 0,
    'tfoot': 0,
    'th': 0,
    'thead': 0,
    'title': _TAG_NOTSKIP,
    'tr': _TAG_STARTP,
    'tt': 0,
    'u': 0,
    'ul': 0,
    'var': _TAG_EM,
    'wbr': 0,
    'xmp': _TAG_PRE,
    # fb2 tags. ignored while parsing
    'emphasis': _TAG_INP,
    'section': _TAG_ID,
    'poem': _TAG_ID,
    'epigraph': _TAG_ID,
}

try:
    import wx

    _IMG_LIB = 'wxPython'


    def convert2png(filename):
        if wx.GetApp() is None:
            _app = wx.PySimpleApp()
        retv = ''
        img = wx.Bitmap(filename, wx.BITMAP_TYPE_ANY)
        if img.Ok():
            img = wx.ImageFromBitmap(img)
            of = tempfile.mktemp()
            if img.SaveFile(of, wx.BITMAP_TYPE_PNG):
                retv = open(of, 'rb').read()
            os.unlink(of)
        return retv
except ImportError:
    try:
        from PIL import Image

        _IMG_LIB = 'PIL'


        def convert2png(filename):
            retv = ''
            try:
                of = tempfile.mktemp()
                Image.open(filename).save(of, 'PNG')
                retv = open(of, 'rb').read()
                os.unlink(of)
            except:
                pass
            return retv
    except ImportError:
        _IMG_LIB = 'None'
        convert2png = None

mimetypes.init()


class MyHTMLParser(SGMLParser):
    """HTML parser.
    Originated from standard htmllib
    """

    from html.entities import name2codepoint
    entitydefs = {}
    for (name, codepoint) in name2codepoint.items():
        entitydefs[name] = chr(codepoint)
    del name, codepoint, name2codepoint
    entitydefs['nbsp'] = ' '

    def reset(self):
        SGMLParser.reset(self)
        self.nofill = 1  # PRE active or not
        self.oldnofill = 0  # for saving nofill flag (for section title, for example)
        self.out = []  # Result
        self.data = ''  # Currently parsed text data
        self.skip = ''  # Skip all all between tags. End tag here
        self.nstack = [[], []]  # Stack for nesting tags control. first el. is tags stack, second - correspond. attrs
        self.save = ''  # Storage for data between tags pair
        self.saving = False  # Saving in progress flag
        self.ishtml = False  # data type
        self.asline = (0, 0, 0)  # [counted lines, > 80, < 80]
        self.ids = {}  # links ids
        self.nextid = 1  # next note id
        self.notes = []  # notes
        self.descr = {}  # description
        self.bins = []  # images (binary objects)
        self.informer = None  # informer (for out messages)
        self.header_stack = []  # tags stack. For example: ['h1','h3','h4'] means: "I am in section under h1, then h3, then h4 header"

    def handle_charref(self, name):
        """Handle decimal escaped character reference, does not handle hex.
        E.g. &#x201c;Quoted.&#x201d; Fred&#x2019;s car."""
        # Modified version of Python 2.3 SGMLParser class
        # to fix &nbsp;, etc. (named escape) ascii decode error
        # as well as &#8220;, etc. (decimal escape) ascii decode error
        try:
            n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return
        self.handle_data(chr(n))

    def process(self, params):
        '''Main processing method. Process all data '''
        self.params = params
        self._TAGS = _TAGS
        if 'informer' in params:
            self.informer = params['informer']
        if params['convert-images'] != 0 and convert2png is None:
            raise RuntimeError

        if self.params['convert-span-to'] == 'emphasis' or self.params['convert-span-to'] == 'em':
            self.params['convert-span-to'] == 'em'
        elif self.params['convert-span-to'] != 'strong':
            self.params['convert-span-to'] = None
        if self.params['convert-span-to'] is not None:
            self._TAGS['span'] = self._TAGS[self.params['convert-span-to']]

        secs = time.time()
        # self.msg('HTML to FictionBook converter, ver. %s\n' % version)
        # self.msg("Reading data...\n")
        data = params['data']
        ##
        ## use basename for href finding, could change regex instead?
        # self.msg('process:'+unicode(params['file-name'], params['sys-encoding']))
        ##self.href_re = re.compile(".*?%s#(.*)" % unicode(params['file-name'], params['sys-encoding']))
        self.href_re = re.compile(".*?%s#(.*)" % str(os.path.basename(params['file-name']) + params['sys-encoding']))
        self.source_directoryname = str(os.path.dirname(params['file-name']) + params['sys-encoding'])
        ##
        try:
            self.header_re = params['header-re'].strip() and re.compile(params['header-re'])
        except:
            self.header_re = None
        if not data:
            return ''
        # self.msg('Preprocessing...\n')
        data = self.pre_process(data)
        # self.msg('Parsing...\n')
        self.feed(data + '</p>')
        self.close()
        # self.msg('Formatting...\n')
        self.detect_epigraphs()
        self.detect_verses()
        self.detect_paragraphs()
        # self.msg('Postprocessing...\n')
        self.post_process()
        # self.msg('Building result document...\n')
        self.out = '<?xml version="1.0" encoding="%s"?>\n' \
                   '<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">\n' % \
                   self.params['encoding-to'] + \
                   (self.make_description() +
                    '<body>%s</body>' % self.out +
                    self.make_notes()) + \
                   self.make_bins() + '</FictionBook>'
        self.msg("Converting has taken %.2f secs\n" % (time.time() - secs))
        return self.out

    # --- Tag handling, need for parsing

    def unknown_starttag(self, tag, attrs):
        '''
        Handle unknown start ttag
        '''
        if tag in self._TAGS or self.skip:
            self.handle_starttag(tag, None, attrs)
        else:
            self.handle_data(self.tag_repr(tag, attrs))

    def unknown_endtag(self, tag):
        '''
        Handle unknown end ttag
        '''
        if tag in self._TAGS or self.skip:
            self.handle_endtag(tag, None)
        else:
            self.handle_data("</%s>" % tag)

    def handle_data(self, data):
        '''
        Handle data stream
        '''
        data = data.replace('&', _CH_REPL_AMP).replace('<', _CH_REPL_LT).replace('>', _CH_REPL_GT)
        if self.saving:
            self.save += data
        else:
            self.data += data

    def handle_starttag(self, tag, method, attrs):
        '''
        Handle all start tags
        '''
        # TODO: make this without 'singletone'
        self.header_tag = tag
        try:
            flag = self._TAGS[tag]
        except:
            flag = 0
        if self.skip and not flag & _TAG_NOTSKIP:
            return
        if flag & _TAG_SKIP:
            self.skip = tag
        if not method:
            if flag & _TAG_EM:
                method = self.start_em
            if flag & _TAG_STRONG:
                method = self.start_strong
            if flag & _TAG_PRE:
                method = self.start_pre
            if flag & _TAG_STARTP:
                method = self.do_p
            if flag & _TAG_HEADER:
                method = self.start_h1
        if method:
            method(attrs)
        # if detected tag, but text still non-html - set text as html
        if not self.ishtml and \
                not flag & (_TAG_EM | _TAG_STRONG | _TAG_INP) and \
                tag != 'h6':
            self.end_paragraph()
            self.ishtml = True
            self.nofill = 0

    def handle_endtag(self, tag, method):
        '''
        Handle all end tags
        '''
        # TODO: make this without 'singletone'
        self.header_tag = tag
        try:
            flag = self._TAGS[tag]
        except:
            flag = 0
        if self.skip and self.skip == tag:
            self.skip = ''
            self.data = ''
            return
        if not method:
            if flag & _TAG_EM:
                method = self.end_em
            if flag & _TAG_STRONG:
                method = self.end_strong
            if flag & _TAG_PRE:
                method = self.end_pre
            if flag & _TAG_ENDP:
                method = self.end_paragraph
            if flag & _TAG_HEADER:
                method = self.end_h1
        if method:
            method()

    def start_title(self, attrs):
        ''' Save document title - start'''
        self.start_saving()

    def end_title(self):
        ''' End saving document title '''
        self.descr['title'] = ' '.join(self.stop_saving().split()).strip()

    def do_meta(self, attrs):
        """
        Handle meta tags - try get document author
        """
        self.descr['author'] = attrs['author']

    def do_p(self, attrs):
        '''Handle tag P'''
        self.end_paragraph()
        self.mark_start_tag('p')

    def start_pre(self, attrs):
        ''' Handle tag PRE '''
        self.nofill = self.nofill + 1
        self.do_p(None)

    def end_pre(self):
        ''' Handle tag /PRE '''
        self.end_paragraph()
        self.nofill = max(0, self.nofill - 1)

    def start_em(self, attrs):
        ''' Handle tag EM '''
        self.mark_start_tag('emphasis')

    def end_em(self):
        ''' Handle tag /EM '''
        self.mark_end_tag('emphasis')

    def start_strong(self, attrs):
        ''' Handle tag STRONG '''
        self.mark_start_tag('strong')

    def end_strong(self):
        ''' Handle tag /STRONG '''
        self.mark_end_tag('strong')

    def start_a(self, attrs):
        ''' Handle tag A '''
        for attrname, value in attrs:
            value = value.strip()
            if attrname == 'href':
                res = self.href_re.match(value)
                if res:
                    value = self.make_id(res.group(1))
                    try:
                        self.ids[value][1] += 1
                    except:
                        self.ids[value] = [0, 1]
                    value = "#" + value
                if self.params['skip-ext-links'] and not res:
                    return
                value = value.replace("&", "&amp;")
                self.mark_start_tag('a', [('xlink:href', value)])
            if attrname == 'name':
                value = self.make_id(value)
                self.data += "<id %s>" % value
                try:
                    self.ids[value][0] += 1
                except:
                    self.ids[value] = [1, 0]

    def end_a(self):
        ''' Handle tag /A '''
        self.mark_end_tag('a')

    def open_section(self):
        self.end_paragraph()
        self.out.extend(['<section>'])
        self.mark_start_tag('p')
        self.oldnofill, self.nofill = self.nofill, 0

    def close_section(self):
        self.end_paragraph()
        self.out.append('</section>')
        self.nofill = self.oldnofill
        self.mark_start_tag('p')

    def open_title(self):
        self.end_paragraph()
        self.out.extend(['<title>'])
        self.mark_start_tag('p')
        self.oldnofill, self.nofill = self.nofill, 0

    def close_title(self):
        self.end_paragraph()
        self.out.append('</title>')
        self.nofill = self.oldnofill
        self.mark_start_tag('p')

    def start_h1(self, attrs):
        ''' Handle tag H1-H6 '''
        # self.end_paragraph()
        # self.out.extend(['</section>','<section>','<title>'])
        # self.mark_start_tag('p')
        # self.oldnofill, self.nofill = self.nofill, 0

        level = int(self.header_tag.replace("h", ""))
        if len(self.header_stack) == 0:
            self.open_section()
            self.open_title()
            self.header_stack.append(level)
        elif self.header_stack[-1] == level:
            self.close_section()
            self.open_section()
            self.open_title()
        elif self.header_stack[-1] < level:
            self.open_section()
            self.open_title()
            self.header_stack.append(level)
        else:
            while True:
                if len(self.header_stack) == 0: break
                if self.header_stack[-1] < level: break
                self.close_section()
                self.header_stack.pop()
            self.open_section()
            self.open_title()
            self.header_stack.append(level)

        # self.close_section()
        # self.open_section()
        # self.open_title()

    def end_h1(self):
        ''' Handle tag /H1-/H6 '''
        # self.end_paragraph()
        # self.out.append('</title>')
        # self.nofill = self.oldnofill
        # self.mark_start_tag('p')
        self.close_title()
        # self.close_section()

    def report_unbalanced(self, tag):
        ''' Handle unbalansed close tags'''
        self.handle_data('</%s>\n' % tag)

    def unknown_charref(self, ref):
        ''' Handle unknown char refs '''
        # FIX: Don't know, how to handle it
        self.msg('Unknown/invalid char ref %s is being ignored\n' % ref)
        raise Warning

    def unknown_entityref(self, ref):
        ''' Handle unknown entity refs '''
        # FIX: Don't know, how to handle it
        self.msg('Unknown entity ref %s\n' % ref, 1)

    # --- Methods for support parsing

    def start_saving(self):
        ''' Not out data to out but save it '''
        self.saving = True
        self.save = ''

    def stop_saving(self):
        ''' Stop data saving '''
        self.saving = False
        return self.save

    def end_paragraph(self):
        '''
        Finalise paragraph
        '''
        if not self.data.strip():
            try:
                p = self.nstack[0].index('p')
                if self.out[-1] == '<p>' or not self.out[-1]:
                    if self.params['skip-empty-lines']:
                        self.out.pop()
                    else:
                        self.out[-1] = "<empty-line/>"
                    self.nstack[0] = self.nstack[0][:p]
                    self.nstack[1] = self.nstack[1][:p]
                else:
                    self.mark_end_tag('p')
            except ValueError:
                pass

        else:
            if 'p' not in self.nstack[0]:
                self.nstack[0][0:0] = 'p'
                self.nstack[1][0:0] = [None]
                self.out.append('<p>')
            self.mark_end_tag('p')

    def mark_start_tag(self, tag, attrs=None):
        ''' Remember open tag and put it to output '''
        try:
            flag = self._TAGS[tag]
        except:
            flag = 0
        if tag in self.nstack[0]:
            self.mark_end_tag(tag)
        self.nstack[0].append(tag)
        self.nstack[1].append(attrs)
        if flag & _TAG_INP:
            self.data += self.tag_repr(tag, attrs)
        else:
            self.out.append(self.tag_repr(tag, attrs))

    def mark_end_tag(self, tag):
        '''
        Close corresponding tags. If tag is not last tag was outed,
        close all previously opened tags.
        I.e. <strong><em>text</strong> -> <strong><em>text</em></strong>
        '''
        if tag not in self.nstack[0]:
            return

        while self.nstack[0]:
            v = self.nstack[0].pop()
            a = self.nstack[1].pop()
            try:
                flag = self._TAGS[v]
            except:
                flag = 0
            if flag & _TAG_INP:
                et = self.tag_repr(v, a)
                if self.data.rstrip().endswith(et):
                    self.data = self.data.rstrip()[:-len(et)]
                    if v == 'a':
                        try:
                            self.ids[a[0][1]][1] -= 1
                        except:
                            pass
                else:
                    self.data += "</%s>" % v
            else:
                self.process_data()
                if self.out[-1] == "<%s>" % v:
                    ## duplicate tag detected, often from replacing embedded <p> inside <a>...</a>
                    ## FIXME not really sure if this is 100% appropriate, is this ONLY for missing target links?
                    self.msg("!!!!\n")
                    self.msg('DEBUG** ' + repr(v) + ' --- ' + repr(self.out[-10:]) + ' ' + repr(v), 1)
                    self.out.pop()
                else:
                    self.out.append("</%s>" % v)
            if tag == v:
                break

    def process_data(self):
        '''
        Handle accomulated data when close paragraph.
        '''
        if not self.data.strip():
            return
        if not self.nofill:
            self.data = _CH_FLOW + self.data.strip()
            self.out.append(self.data)
        else:
            self.data = self.process_pre(self.data)
            self.data = self.detect_headers(self.data)
            try:
                if self.data[0] == '</p>' and self.out[-1] == '<p>':
                    self.out.pop()
                    self.data = self.data[1:]
            except IndexError:
                pass
            self.out.extend(self.data)
        self.data = ''

    # --- Parsed data processing methods

    def pre_process(self, data):
        '''
        Processing data before parsing.
        Return data converted to unicode. If conversion is impossible, return None.
        If encoding not set, try detect encoding with module recoding from pETR project.
        '''
        encoding = self.params['encoding-from']
        if not encoding:
            try:
                data = str(data, 'utf8')
                encoding = None  # No encoding more needed
            except UnicodeError:
                try:
                    import recoding  # try import local version recoding
                    encoding = recoding.GetRecoder().detect(data[:2000])
                except ImportError:
                    try:
                        import petr.recoding as recoding  # try import pETR's modyle
                        encoding = recoding.GetRecoder().detect(data[:2000])
                    except ImportError:
                        encoding = None
                if not encoding:
                    encoding = "Windows-1251"
                    self.msg("Recoding module not found. Use default encoding")
        try:
            if encoding:
                data = str(data, encoding)
                self.params['encoding-from'] = encoding
        except:
            data = None
            self.msg("Encoding %s is not valid\n" % encoding)
        if data:
            data = data.replace('\x0e', '<h6>').replace('\x0f', '</h6>')
            for i in '\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x10\x11' \
                     '\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f':
                data = data.replace(i, ' ')

        return data

    def post_process(self):
        '''
        Last processing method
        '''
        id = ''
        for i in range(len(self.out)):
            if not self.out[i]:
                pass  # skip empty lines (can apper below, where ...out[i+1]='')
            elif self.out[i][0] != '<':
                id, p = self.process_paragraph(self.out[i], id)
                if p:
                    if id:
                        self.out[i - 1] = '<%s id="%s">' % (self.out[i - 1][1:-1], id)
                        id = ''
                    self.out[i] = p
                else:
                    self.out[i - 1] = self.out[i] = self.out[i + 1] = ''  # remove empty paragraph
            elif id:
                try:
                    if self._TAGS[self.out[i][1:-1]] & _TAG_ID:
                        self.out[i] = '<%s id="%s">' % (self.out[i][1:-1], id)
                        id = ''
                except KeyError:
                    pass
        self.out = '\n'.join(self.out). \
            replace(_CH_REPL_AMP, '&amp;'). \
            replace(_CH_REPL_LT, '&lt;'). \
            replace(_CH_REPL_GT, '&gt;'). \
            replace('...', _CH_DOTS). \
            strip()
        if self.params['convert-hyphen']:
            self.out = self.out.replace("- ", _CH_TIRE + " ").replace(" -", " " + _CH_TIRE)

        # delete links withself.out anchors
        for i in [x for x in list(self.ids.keys()) if not self.ids[x][0] and self.ids[x][1] >= 0]:
            self.out = re.sub("%s(.*?)%s" % (self.tag_repr('a', [('xlink:href', '#' + i)]), '</a>'), r'\1', self.out)
        sect = self.out.find('<section')
        close_level = len(self.header_stack)
        close_level = close_level + 1  # This is made for strange heuristics below
        if 0 < sect < len(self.out) / 3 and self.params['detect-annot']:
            self.descr['annot'] = ' '.join(self.out[:sect].rstrip().rstrip('</section>').split())
            self.out = self.out[sect:]
        else:
            if self.out.startswith('</section>'):
                self.out = self.out[len('</section>'):]
            elif self.out.startswith("<section>"):
                close_level = close_level - 1
            else:
                self.out = '<section>' + self.out
        for i in range(close_level): self.out += '</section>'
        self.out = _RE_EL.sub(r'\1', self.out)

    def detect_headers(self, data):
        '''
        Find headers in plain text.
        '''
        if not self.params['detect-headers']:
            return [data]
        res = []
        pstart = i = 0
        header = ['</p>',
                  '</section>',
                  '<section>',
                  '<title>',
                  '<p>',
                  '',  # place for title (5)
                  '</p>',
                  '</title>',
                  '<p>']
        while i < len(data) - 1:
            empty0 = not data[i]
            try:
                empty1 = not data[i + 1]
                empty2 = not data[i + 2]
                empty3 = not data[i + 3]
            except IndexError:
                empty1 = empty2 = empty3 = False
            if empty0 and empty1 and not empty2 and empty3:
                res.append(data[pstart:i])
                header[5] = _CH_FLOW + data[i + 1].strip()
                res.extend(header)
                i += 2
                pstart = i + 2
            else:
                istitle = (
                        empty0 and
                        not empty1 and
                        empty2 and
                        (
                                empty3 or
                                data[i + 1].startswith(' ' * 8) or
                                data[i + 1].isupper() or
                                (
                                        data[i + 1].lstrip()[0] not in _DIAL_START and
                                        data[i + 1][-1] not in _SENTENCE_FIN
                                ) or
                                data[i + 1].lstrip()[0] in _HEAD_CHARS or
                                self.is_roman_number(data[i + 1])
                        )
                )
                istitle = istitle or \
                          not empty1 and \
                          self.header_re and \
                          self.header_re.match(data[i + 1])
                if istitle:
                    res.append(data[pstart:i])
                    header[5] = _CH_FLOW + data[i + 1].strip()
                    res.extend(header)
                    i += 1
                    while i < len(data) - 1 and not data[i + 1]:
                        i += 1
                    pstart = i + 1
            i += 1
        if pstart < len(data):
            res.append(data[pstart:])
        return res

    def detect_epigraphs(self):
        '''
        Detect epigraphs (in plain text)
        '''
        if not self.params['detect-epigraphs']:
            return
        sect_found = 0
        i = 0
        while i < len(self.out):
            if type(self.out[i]) != list:
                if self.out[i] == '<section>':
                    sect_found = 1
                elif self.out[i] == '<title>':
                    sect_found = sect_found and 2 or 0
                elif self.out[i] == '</title>':
                    sect_found = sect_found and 1 or 0
                elif self.out[i][0] != '<':
                    sect_found = sect_found != 1 and 2 or 0
            else:
                if sect_found == 1:
                    res = []
                    raw = self.out[i]
                    lraw = len(raw)
                    j = 0
                    eplines = 0
                    epfound = 0
                    while j < len(raw):
                        while j < lraw and not raw[j]:
                            j += 1  # skip empty lines
                        eep = -1
                        # search empty line
                        for k in range(j, j + 60):
                            if k >= lraw or not raw[k]:
                                eep = k
                                break
                        if eep == j:
                            break
                        if eep >= 0:
                            eplines = 0
                            for k in range(j, eep):
                                rawk = raw[k].lstrip()
                                if ' ' * 10 in raw[k] or len(rawk) < 60:
                                    eplines += 1
                                if len(rawk) > 60:
                                    eplines -= 5
                                if rawk and (
                                        rawk[0] in _DIAL_START or
                                        rawk[0].isdigit() and
                                        len(rawk) > 2 and
                                        rawk[1] in _DIAL_START2
                                ):
                                    eplines -= 1
                            if (float(eplines) / (eep - j) > 0.8):
                                epfound += 1
                                author = eep - j > 1
                                res.extend(['<epigraph>', '<p>', raw[j:eep - author]])
                                if author and self.clean_str(raw[eep - 1]).lstrip()[0].isupper():
                                    res.extend(
                                        ['</p>', '<text-author>', _CH_FLOW + self.clean_str(raw[eep - 1]).lstrip(),
                                         '</text-author>'])
                                else:
                                    if author:
                                        res[-1].append(raw[eep - 1])
                                    res.append('</p>')
                                res.append('</epigraph>')
                                j = eep
                            else:
                                eep = -1
                        if eep < 0:
                            break
                        j += 1
                    if epfound:
                        istart = i
                        iend = i + 1
                        if i and self.out[i - 1] == '<p>':
                            istart -= 1
                        if j < len(raw) - 1:
                            res.extend(['<p>', raw[j:]])
                        elif i < len(self.out) - 1 and self.out[i + 1] == '</p>':
                            iend += 1
                        self.out[istart:iend] = res
                        i = istart + len(res) - 1
                sect_found = 0
            i += 1

    def detect_verses(self):
        '''
        Detect verses in plain text
        '''
        if not self.params['detect-verses']:
            return
        i = 0
        while i < len(self.out):
            if type(self.out[i]) == list:
                res = []
                raw = [self.clean_str(x).rstrip() for x in self.out[i]]
                lraw = len(raw)
                pfound = jstart = j = 0
                while j < lraw - 3:
                    if raw[j] and len(raw[j]) < 60 and \
                            raw[j + 1] and len(raw[j + 1]) < 80 and \
                            raw[j + 2] and len(raw[j + 2]) < 80 and \
                            raw[j + 3] and len(raw[j + 3]) < 80:
                        fl = len(raw[j])
                        k = j
                        while k < lraw:
                            if raw[k].strip() and (
                                    abs(len(raw[k]) - fl) > 15 or
                                    raw[k].lstrip()[0] in _DIAL_START
                            ):
                                break
                            k += 1
                        if k - j > 3:
                            pfound += 1
                            if jstart:
                                res.append('<p>')
                            if jstart != j:
                                res.extend([self.out[i][jstart:j], '</p>'])
                            res.extend(['<poem>', '<stanza>'])
                            for l in range(j, k):
                                if raw[l]:
                                    res.extend(['<v>', raw[l].lstrip(), '</v>'])
                                elif l < k - 1 and res[-1] != '<stanza>':
                                    res.extend(['</stanza>', '<stanza>'])
                            res.extend(['</stanza>', '</poem>'])
                            j = k - 1
                            jstart = k
                    j += 1
                if pfound:
                    if jstart < lraw - 1:
                        res.extend(['<p>', self.out[i][jstart:]])
                    istart = i
                    iend = i + 1
                    try:
                        if res[0] == '<poem>' and self.out[i - 1] == '<p>':
                            istart -= 1
                    except:
                        pass
                    try:
                        if res[-1] == '</poem>' and self.out[i + 1] == '</p>':
                            iend += 1
                    except:
                        pass
                    self.out[istart:iend] = res
            i += 1

    def detect_paragraphs(self):
        '''
        Detect paragraphs in plain text
        '''
        i = 0
        while i < len(self.out):
            if type(self.out[i]) == list:
                res = []
                raw = self.out[i]
                j = 0
                pfound = 0
                while j < len(raw) and not raw[j]:
                    j += 1
                jstart = j
                while j < len(raw):
                    if not raw[j]:
                        try:
                            while not raw[j]:
                                j += 1
                        except IndexError:
                            break
                        if not self.params['skip-empty-lines']:
                            res.append('<empty-line/>')
                        jstart = j
                        continue
                    elif self.asline or \
                            not self.params['detect-paragraphs'] or \
                            j >= len(raw) - 1 or \
                            not raw[j + 1].lstrip() or \
                            (raw[j + 1].lstrip()[0] in _DIAL_START or \
                             raw[j + 1].startswith('  ')
                            ) and raw[j][-1] in _SENTENCE_FIN:
                        pfound += 1
                        res.extend(['<p>', _CH_FLOW + '\n'.join(raw[jstart:j + 1]), '</p>'])
                        jstart = j + 1
                    j += 1
                if pfound > 0:
                    self.out[i:i + 1] = res[1:-1]
                    i += len(res) - 2
                else:
                    self.out[i] = '\n'.join(raw).lstrip()
            i += 1

    def detect_italic(self, text, arg):
        signs = '_.,!?:'
        istart = -1
        res = ''
        while True:
            istart = text.find('_')
            if istart >= 0:
                iend = sys.maxsize
                for i in signs:
                    try:
                        iend = min(iend, text.index(i, istart + 1))
                    except:
                        pass
                if iend == sys.maxsize:
                    iend = 0
                text = text[:istart] + \
                       '<emphasis>' + \
                       text[istart + 1:iend or None] + \
                       '</emphasis>' + \
                       (iend and text[iend + (text[iend] == '_'):] or '')
            else:
                break
        return text

    def detect_notes(self, text, arg):
        while True:
            snote = text.find(arg[0])
            enote = text.find(arg[1])
            if snote < 0 or enote <= snote:
                break
            self.notes.append((self.nextid, text[snote + 1:enote]))
            text = (text[:snote] +
                    '<a xlink:href="FictionBookId%s" type="note">' % self.nextid +
                    "note %s" % self.nextid + "</a>" +
                    text[enote + 1:]
                    )
            self.nextid += 1
        return text

    def process_pre(self, data):
        '''
        Process preformatted data (data between <pre> and </pre> tag or plain text file)
        Determine text format.
        '''
        data = [x.rstrip() for x in data.splitlines()]
        if type(self.asline) == tuple:
            count, G80, L80 = self.asline
            for i in data:
                if len(i) > 80:
                    G80 += 1
                else:
                    L80 += 1
                count += 1
                if count > 2000:
                    self.asline = G80 > L80
                    break
            if type(self.asline) == tuple:
                self.asline = (count, G80, L80)
        return data

    def process_paragraph(self, paragraph, id):
        '''
        Process paragraph. Find id, normalize quotes.
        '''
        paragraph = paragraph.strip()
        startp = paragraph.find('<id ')
        while startp >= 0:
            endp = paragraph.index('>',
                                   startp + 4)  # if '>' will not be found exception  will raised, because use index
            found_id = paragraph[startp + 4:endp]
            if not id:
                id = found_id
            else:
                self.ids[found_id][0] = 0
            paragraph = paragraph[:startp] + paragraph[endp + 1:]
            startp = paragraph.find('<id ')
        # id here is paragraph id, if found
        if not paragraph:
            return [id, '']
        # strip leading spaces if paragraph starth with tag
        if paragraph[0] == '<':
            endp = paragraph.index('>')
            paragraph = paragraph[:endp + 1] + paragraph[endp + 1:].lstrip()
        if self.params['convert-quotes']:
            # process quotes
            paragraph = _RE_LQUOTES.sub(_CH_LEFT_Q, paragraph)
            paragraph = _RE_RQUOTES.sub(_CH_RIGHT_Q, paragraph)
            paragraph = _RE_LQUOTES2.sub(_CH_LEFT_Q, paragraph)
            paragraph = _RE_RQUOTES2.sub(_CH_RIGHT_Q, paragraph)
        if self.params['detect-notes']:
            paragraph = self.process_nontags(paragraph, self.detect_notes, "[]")
            paragraph = self.process_nontags(paragraph, self.detect_notes, "{}")
        if self.params['detect-italic']:
            paragraph = self.process_nontags(paragraph, self.detect_italic, None)
        paragraph = ' '.join(paragraph.split())  # Remove extra whitespaces

        return [id, paragraph]

    def process_nontags(self, text, func, arg):
        ss = 0
        res = ''
        w = ''
        while 0 <= ss < len(text):
            try:
                i = text.index('<', ss)
                w = text[ss:i]
                ss = i
            except:
                w = text[ss:]
                ss = -1
            if w.strip():
                # process text between tagtext if any.
                res += func(w, arg)
            else:
                res += ' '
            if ss >= 0:
                i = text.index('>', ss)
                res += text[ss:i + 1]
                ss = i + 1
        return res

    # --- Make out document methods

    def make_description(self):
        author = 'author' in self.descr and self.descr['author'] or ''
        title = 'title' in self.descr and self.descr['title'] or ''
        if not author and '.' in title:
            point = title.index('.')
            author = title[:point].strip()
            title = title[point + 1:].strip()
        author = author.split()
        first_name = author and author[0] or ''
        last_name = len(author) > 2 and author[2] or (len(author) > 1 and author[1] or '')
        retv = '<description><title-info><genre></genre><author><first-name>%s' \
               '</first-name><last-name>%s</last-name></author>' \
               '<book-title>%s</book-title>' % (first_name, last_name, title)
        if 'annot' in self.descr:
            retv += '<annotation>%s</annotation>' % self.descr['annot']
        retv += '</title-info><document-info><author><nickname></nickname></author>' \
                '<date value="%s">%s</date>' \
                '<id>%s</id>' \
                '<version>1.0</version>' \
                '<program-used>Books Downloader ver. %s</program-used>' \
                '</document-info></description>' % \
                (time.strftime('%Y-%m-%d'),
                 str(time.strftime('%d %B %Y, %H:%M') + self.params['sys-encoding']),
                 oct(int(time.time())),
                 version)
        return retv

    def make_notes(self):
        if not self.notes:
            return ''
        retv = ['<section id="FictionBookId%s"><title><p>note %s</p></title>%s</section>' %
                (x, x, y) for x, y in self.notes]
        return '<body name="notes"><title><p>Notes</p></title>' + ''.join(retv) + '</body>'

    def make_bins(self):
        if not self.bins:
            return ''
        # return ''.join(['<binary content-type="image/jpeg" id="%s">%s</binary>' % \
        # (x.encode(self.params['encoding-to'],'xmlcharrefreplace'),y) for x,y in self.bins])
        return ''.join(['<binary content-type="%s" id="%s">%s</binary>' % \
                        (mime_type, x, y) for mime_type, x, y in self.bins])

    # --- Auxiliary  methods

    def tag_repr(self, tag, attrs, single=False):
        ''' Start tag representation '''
        closer = single and '/' or ''
        if attrs:
            return "<%s %s%s>" % (tag, ' '.join(['%s="%s"' % x for x in attrs if x[1] is not None]), closer)
        else:
            return "<%s%s>" % (tag, closer)

    def clean_str(self, intext):
        ''' Remove simple tags from line. '''
        return _RE_TAG.sub('', intext)

    def is_roman_number(self, instr):
        '''
        Detect - is instr is roman number
        '''
        instr = self.clean_str(instr).strip()
        if len(instr) > 8:
            return False
        return bool(_RE_ROMAN.match(instr))

    def msg(self, msg):
        if self.informer:
            self.informer(msg)

    def make_id(self, id):
        '''
        Make properly link id
        '''
        # FIX: make id later
        return id

    def print_out(self, data=None):
        if data is None:
            data = self.out
        for i in data:
            if type(i) == list:
                print()
                '['
                for j in i:
                    print()
                    j.encode('koi8-r', 'replace')
                print()
                ']'
            else:
                print()
                i.encode('koi8-r', 'replace')

    def convert_image(self, filename):
        mime_type = mimetypes.guess_type(filename)[0]
        image_filename = os.path.join(self.source_directoryname, filename)
        ## note if mime_type is None, unable to determine type....
        if not self.params['convert-images']:
            if "http://" in image_filename or "https://" in image_filename:
                # f = urllib2.urlopen(image_filename)
                # data = f.read()
                print(("Downloading image:" + image_filename))
                data = None
            else:
                f = open(image_filename, 'rb')
                data = f.read()
                f.close()
        else:
            data = convert2png(image_filename)
            mime_type = 'image/png'
        if data:
            data = base64.encodestring(data)
        return mime_type, data


def usage():
    print(
        '''
HTML to FictionBook converter, ver. %s
Usage: h2fb2.py [options]
where options is:
    -i, --input-file         Input file name(stdin)
    -o, --output-file        Output file name(stdout)
    -f, --encoding-from      Source encoding(autodetect)
    -t, --encoding-to        Result encoding(Windows-1251)
    -h, --help               This help
    -r,  --header-re         Regular expression for headers detection('')
    --not-convert-quotes     Not convert quotes
    --not-convert-hyphen     Not convert hyphen
    --skip-images            Skip messages
    --skip-ext-links         Skip external links
    --allow-empty-lines      Allow generate tags <empty-line/>
    --not-detect-italic      Not detect italc
    --not-detect-headers     Not detect sections headers
    --not-detect-epigraphs   Not detect epigraphs
    --not-detect-paragraphs  Not detect paragraphs
    --not-detect-annot       Not detect annotation
    --not-detect-verses      Not detect verses
    --not-detect-notes       Not detect notes
''' % version)


# FIXME TODO, the try block is broken
locale.setlocale(locale.LC_ALL, '')
try:
    sys_encoding = locale.nl_langinfo(locale.CODESET)
except AttributeError:
    sys_encoding = "Windows-1251"

params = {
    'file-name': '',
    # Input HTML file name, even if not reading from an on-disk file, this should be passed in to aid in href detection
    'data': '',  # Data for processing
    'encoding-from': '',  # Source data encoding
    'encoding-to': 'Windows-1251',  # Result data encoding
    'convert-quotes': True,  # Convert "" to << >>
    'convert-hyphen': True,  # Convert - to ndash
    'header-re': '',  # regexp for detecting section headers
    'skip-images': False,  # Ignore images (not include it to result)
    'skip-ext-links': False,  # Ignore external links
    'skip-empty-lines': True,  # Not generate <empty-line/> tags
    'detect-italic': True,  # Detect italc (_italic text here_)
    'detect-headers': True,  # Detect sections headers
    'detect-epigraphs': True,  # Detect epigraphs
    'detect-paragraphs': True,  # Detect paragraphs
    'detect-annot': True,  # Detect annotation
    'detect-verses': True,  # Detect verses
    'detect-notes': False,  # Detect notes ([note here] or {note here})
    'convert-images': True,  # Force convert of images to png or not
    'sys-encoding': sys_encoding,
    'informer': sys.stderr.write,
    'convert-span-to': None,
    # what to convert span tags to, if set to 'em' or 'emphasis' converts spans to 'emphasis', if 'strong' converts to 'strong', anything else is ignored/skipped/removed (silently)
}


def convert_to_fb(opts):
    parser = argparse.ArgumentParser(description='Converting from HTML to FB2')
    parser.add_argument('input_file', type=argparse.FileType('rb'), help='Input for file', default=sys.stdin)
    parser.add_argument('output_file', nargs='?', type=argparse.FileType('w'),
                        help='Output for file', default=None)
    parser.add_argument('-f', '--encoding-from', help='Source encoding(autodetect)')
    parser.add_argument('-t', '--encoding-to', help='Result encoding(Windows-1251)')
    parser.add_argument('-a', '--author', type=str, help='Author in format(Name LastName)')
    parser.add_argument('--not-convert-quotes', action='store_false')
    parser.add_argument('--not-convert-hyphen', action='store_false')
    parser.add_argument('--skip-images', action='store_false')
    parser.add_argument('--skip-ext-links', action='store_true')
    parser.add_argument('--allow-empty-lines', action='store_false')
    parser.add_argument('--not-detect-italic', action='store_false')
    parser.add_argument('--not-detect-headers', action='store_false')
    parser.add_argument('--not-detect-epigraphs', action='store_false')
    parser.add_argument('--not-detect-paragraphs', action='store_false')
    parser.add_argument('--not-detect-annot', action='store_false')
    parser.add_argument('--not-detect-verses', action='store_false')
    parser.add_argument('--not-detect-notes', action='store_false')
    parser.add_argument('--not-convert-images', action='store_false')
    args = parser.parse_args()
    in_file = args.input_file
    out_file = open(f"{args.input_file.name.split('.')[0]}.fb2", 'w', encoding='utf-8') if args.output_file is None else args.output_file
    if args.encoding_from is not None:
        params['encoding-from'] = args.encoding_from
    if args.encoding_from is not None:
        params['encoding-to'] = args.encoding_to
    if args.encoding_from is not None:
        params['convert-quotes'] = args.encoding_to

    params['data'] = in_file.read()
    in_file.close()
    os.remove(in_file.name)
    p = MyHTMLParser()
    p.do_meta({'author': args.author})
    data = p.process(params)
    out_file.write(data)
    out_file.close()


if __name__ == '__main__':
    convert_to_fb(sys.argv[1:])
