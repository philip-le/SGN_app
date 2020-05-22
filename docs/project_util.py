#
# Utility functions 


import html2text
h = html2text.HTML2Text()
h.ignore_links = True




# A HTML escape code -> text decoding table
HTML_ESCAPE_DECODE_TABLE = { "#39"   : "\'",
                             "quot"  : "\"",
                             "#34"   : "\"",
                             "amp"   : "&",
                             "#38"   : "&",
                             "lt"    : "<",
                             "#60"   : "<",
                             "gt"    : ">",
                             "#62"   : ">",
                             "nbsp"  : " ",
                             "#160"  : " "   }

def translate_html(html_fragment):
    """
    Translates a HTML fragment to plain text.

    html_fragment: string (ascii or unicode)
    returns: string (ascii)
    """
    test_array = h.handle(html_fragment).replace("\n", " ")
    if len(test_array)<50:
        test_array=''
    return test_array

def unicode_to_ascii(s):
    """
    converts s to an ascii string.
    
    s: unicode string
    """
    ret = ""
    for ch in s:
        try:
            ach = str(ch)
            ret += ach
        except UnicodeEncodeError:
            ret += "?"
    return ret

