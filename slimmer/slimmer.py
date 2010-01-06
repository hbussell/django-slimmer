"""
 slimmer.py
 Peter Bengtsson, mail@peterbe.com, 2004

 slimmer.py is a simple set of functions for compressing/optimizing
 HTML, XHTML and CSS documents as strings.
 Ideally used from other modules used something like this::

  >>> import slimmer
  >>> code = open('file.html').read()
  >>> slimmed = slimmer.xhtml_slimmer(code)
  >>> print len(code), len(slimmed)

 You have to estimate yourself if you think it's worth using slimmer
 on your documents if you're running a dynamic setting such as a
 web application (e.g. Zope with CheckoutableTemplates).
 On my PC I slimmed a 1MB .html document in 2.2 seconds and saved
 100KB. Saved 31KB on a 110KB .css file in 0.063 seconds.
 And lastly, saved 17% in size in 0.016 seconds for www.python.org.
 

Changes::

 0.1.2      Sep 2004    Added basic CLI functions (see run())

 0.1.1      Sep 2004    Major speed improvment by removing
                        the unquote_numerical feature.
                        
 0.1.0      Sep 2004    First version numbering
"""

__version__='0.1.2'
__all__=['acceptableSyntax','slimmer','css_slimmer',
         'html_slimmer','xhtml_slimmer']

import re, os


# Define the syntax options we accept
HTML = 'html'
XHTML = 'xhtml'
CSS = 'css'

OK_SYNTAX = (HTML, XHTML, CSS)

def acceptableSyntax(syntax):
    """ return the syntax as we recognize it or None """
    syntax = str(syntax).lower().strip().replace(' ','').replace('-','')
    syntax = syntax.replace('stylesheet','css') # allow for alias
    if syntax in OK_SYNTAX:
        return syntax
    else:
        return None

def slimmer(code, syntax=XHTML):
    """ wrap all function we have """
    if syntax == XHTML:
        return _xhtml_slimmer(code)
    elif syntax == HTML:
        return _html_slimmer(code)
    elif syntax == CSS:
        return _css_slimmer(code)

# CSS
css_comments = re.compile(r'/\*.*?\*/', re.MULTILINE|re.DOTALL)
hex_colour = re.compile(r'#\w{2}\w{2}\w{2}')
    
def _css_slimmer(css):
    """ remove repeating whitespace ( \t\n) """

    css = css_comments.sub('', css) # remove comments
    css = re.sub(r'\s\s+', '', css) # >= 2 whitespace becomes no whitespace
    css = re.sub(r'\s+{','{', css) # no whitespace until start of selector
    css = re.sub(r'\s}','}', css) # no whitespace until end of selector
    css = re.sub(r'{\s+', '{', css) # whatspace after {
    css = re.sub(r':\s+',':', css) # no whitespace after colon
    css = re.sub(r';\s+',';', css) # no whitespace in '#fff;  color...'
    css = re.sub(r',\s',r',', css) # no extraspace between commas
    css = re.sub(r'\s+</',r'</', css, re.MULTILINE) # no extraspace before </style>
    css = re.sub(r'}\s+(\w|#)', r'}\1', css)
#    css = re.sub(r'}\s+(\w)', r'}\1', css)
    css = re.sub(r';}', r';}\n', css) # ok to have a linebreak here
    css = simplifyHexColours(css)

    return css.strip()


# HTML
f_IMD = re.I|re.MULTILINE|re.DOTALL
f_MD = re.MULTILINE|re.DOTALL
f_M = re.MULTILINE

html_comments_oneline = re.compile(r'<!--.*?-->')

html_inline_css = re.compile(r'<style.*?>.*?</style>', f_IMD)

any_tag = re.compile(r"<\w.*?>", f_IMD)
excess_whitespace = re.compile(r' \s+|\s +', f_M)
excess_whitespace1 = re.compile(r'\w\s+\w', f_M)
excess_whitespace2 = re.compile(r'"\s+>', f_M)
excess_whitespace3 = re.compile(r"'\s+>", f_M)
excess_whitespace4 = re.compile('"\s\s+\w+="|\'\s\s+\w+=\'|"\s\s+\w+=|\'\s\s+\w+=', f_M)
excess_whitespace6 = re.compile(r"\d\s+>", f_M)

def _xhtml_slimmer(xhtml):
    # optimize inline CSS
    return _html_slimmer(xhtml)

def _html_slimmer(html):
    """ Optimize like XHTML but go one step further """
    # 1. optimize inline CSS
    for styletag in html_inline_css.findall(html):
	html = html.replace(styletag, css_slimmer(styletag))
	
    # 2. Remove excessive whitespace between tags
    html = re.sub(r'>\s+<','><', html)
    
    # 3. Remove oneline comments
    html = html_comments_oneline.sub('', html)
    
    # 4. In every tag, remove quotes on numerical attributes and all
    # excessive whitespace
    
    ew1 = excess_whitespace1 # shortcut
    ew6 = excess_whitespace6 # shortcut
    ew4 = excess_whitespace4 # shortcut

    for tag in uniqify(any_tag.findall(html)):
	# 4a. observe exceptions
	if tag.startswith('<!') or tag.find('</')>-1:
	    continue
	original = tag
	
	# 4b. remove excess whitespace inside the tag
	tag= excess_whitespace2.sub('">', tag)
	tag= excess_whitespace3.sub("'>", tag)
	
	for each in ew1.findall(tag)+ew6.findall(tag):
	    tag = tag.replace(each, excess_whitespace.sub(' ',each))
	for each in ew4.findall(tag):
	    tag = tag.replace(each, each[0]+' '+each[1:].lstrip())
	
	
	# has the tag been improved?
	if original != tag:
	    html = html.replace(original, tag)
    
    
    return html.strip()


## ----- Some fancier names
##

def css_slimmer(css):
    return _css_slimmer(css)

def xhtml_slimmer(xhtml):
    return _xhtml_slimmer(xhtml)

def html_slimmer(html):
    return _html_slimmer(html)


## ----- Methods related to simplifying HEX colour codes

def uniqify(all):
    """ borrowed from Tim Peters' algorithm on ASPN Cookbook """
    # REMEMBER! This will shuffle the order of the list
    u = {}
    for each in all:
        u[each]=1
    return u.keys()

def simplifyHexColours(text):
    """ Replace all colour declarations where pairs repeat.
    I.e. #FFFFFF => #FFF; #CCEEFF => #CEF
    and #EFEFEF, #EFCDI9 avoided """
    colour_replacements = {}
    all_hex_encodings = hex_colour.findall(text)

    for e in uniqify(all_hex_encodings):
        if e[1]==e[2] and e[3]==e[4] and e[5]==e[6]:
            colour_replacements[e] = '#'+e[1]+e[3]+e[5]
    mreplacer = MultiReplacer(colour_replacements)
    return mreplacer(text)

class MultiReplacer:
    def __init__(self, replacements, delimiter='\t', wholeWords=None, caseInsensitive=None):
        # Build replacements dictionary - may come in as a mapping or as a file         
        self.replacements = {}
        try:
            # replacements is a mapping
            self.replacements.update(replacements)
        except TypeError:
            # replacements is a file
            replacementsFile = open(replacements, 'r')
            for line in replacementsFile.readlines():
                fromValue, toValue = line.split(delimiter)[:2] # Split line
                
                while toValue[-1] in '\r\n': # Strip newlines
                    toValue = toValue[:-1]

                self.replacements[fromValue] = toValue # Add to dictionary
            replacementsFile.close()
  
        # Build char to char mapping...
        self.charMap = None
        if not wholeWords:
            charMap = map(chr, range(256))
            for fromValue, toValue in self.replacements.items():
                if len(fromValue) <> 1 or len(toValue) <> 1:
                    break
                if caseInsensitive:
                    charMap[ord(fromValue.upper())] = toValue
                    charMap[ord(fromValue.lower())] = toValue
                else:
                    charMap[ord(fromValue)] = toValue
            else:
                self.charMap = "".join(charMap)
                return

        # String to string mapping - use a regular expression
        import re
        fromVals = self.replacements.keys()
        fromVals.sort()

        # Build regexp pattern
        if not wholeWords:
            rePattern = '|'.join(map(re.escape, fromVals))
        else:
            rePattern = r'\b(' \
                      + '|'.join(map(re.escape, fromVals)) + r')\b'
        
        # Compile regexp
        if caseInsensitive: 
            self.reObject = re.compile(rePattern, re.I)
        else:
            self.reObject = re.compile(rePattern)

    def __call__(self, string):
        # apply replacement to string
        
        # Char to char mapping
        if self.charMap: 
            return string.translate(self.charMap)

        # String to string mapping        
        return self.reObject.sub(self.__replaceMatch, string)
    
    def __replaceMatch(self, match):
        item = match.group(0)
        return self.replacements.get(item)


def __grr():
    print "Usage: python slimmer.py /path/to/input.html [xhtml|html|css] /path/to/output.html"
    sys.exit(1)

def __guess_syntax(filepath):
    lines = []
    if os.path.isfile(filepath):
        if filepath.lower().endswith('.css'):
            return 'css'
        f=open(filepath)
        line = f.readline()
        while len(lines) < 15 and line:
            lines.append(line)
            line = f.readline()
        f.close()
        lines = '\n'.join([x for x in lines if x.find('!DOCTYPE')>-1])
        if lines.find('HTML 4.0')>-1:
            return 'html'
        elif lines.find('XHTML 1.0')>-1:
            return 'xhtml'
    return None

def cmd_run(cmdargs):
    outfilepath = None
    if len(cmdargs)==3:
        outfilepath = cmdargs[2]
        cmdargs=cmdargs[:-1]

    if len(cmdargs)==2 and os.path.isfile(cmdargs[1]):
        filepath, outfilepath = cmdargs
        syntax = __guess_syntax(filepath)
    elif len(cmdargs)==2:
        filepath, syntax = cmdargs
    elif len(cmdargs)==1:
        filepath = cmdargs[0]
        syntax = __guess_syntax(filepath)
    else:
        return __grr()

    if acceptableSyntax(syntax) and os.path.isfile(filepath):
        from time import time
        t0=time()
        slimmed = slimmer(open(filepath).read(), syntax)
        t1=time()-t0
        if outfilepath:
            print "Took", t1, "seconds"
            fw=open(outfilepath,'w')
            fw.write(slimmed)
            fw.close()
            del slimmed
        else:
            print slimmed
    else:
        return __grr()
    
    
if __name__=='__main__':
    import sys, os
    cmd_run(sys.argv[1:])
