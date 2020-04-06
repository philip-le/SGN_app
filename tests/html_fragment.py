html_fragment = '<ol><li><a href="https://news.google.com/__i/rss/rd/articles/CBMiKmh0dHBzOi8vd3d3LmJiYy5jby51ay9uZXdzL2hlYWx0aC01MjE5MzI2NNIBLmh0dHBzOi8vd3d3LmJiYy5jby51ay9uZXdzL2FtcC9oZWFsdGgtNTIxOTMyNjQ?oc=5" target="_blank">Coronavirus: What is intensive care and which patients need it?</a>&nbsp;&nbsp;<font color="#6f6f6f">BBC News</font></li><li><a href="https://news.google.com/__i/rss/rd/articles/CBMiJmh0dHBzOi8vd3d3LmJiYy5jby51ay9uZXdzL3VrLTUyMTkyNjA00gEqaHR0cHM6Ly93d3cuYmJjLmNvLnVrL25ld3MvYW1wL3VrLTUyMTkyNjA0?oc=5" target="_blank">Coronavirus: Boris Johnson moved to intensive care as symptoms worsen</a>&nbsp;&nbsp;<font color="#6f6f6f">BBC News</font></li><li><a href="https://news.google.com/__i/rss/rd/articles/CBMid2h0dHBzOi8vd3d3LnRoZXRpbWVzLmNvLnVrL2FydGljbGUvY29yb25hdmlydXMtbm8tMTAtYXR0YWNrcy1ydXNzaWFuLWZha2UtbmV3cy1hYm91dC1ib3Jpcy1qb2huc29uLXZlbnRpbGF0b3ItcTczcW03ZjZz0gEA?oc=5" target="_blank">No 10 attacks Russian claims of Boris Johnson ventilator</a>&nbsp;&nbsp;<font color="#6f6f6f">The Times</font></li><li><a href="https://news.google.com/__i/rss/rd/articles/CBMiU2h0dHBzOi8vd3d3LnRlbGVncmFwaC5jby51ay9vcGluaW9uLzIwMjAvMDQvMDYvd2lzaC1wcmltZS1taW5pc3Rlci1zcGVlZHktcmVjb3Zlcnkv0gFXaHR0cHM6Ly93d3cudGVsZWdyYXBoLmNvLnVrL29waW5pb24vMjAyMC8wNC8wNi93aXNoLXByaW1lLW1pbmlzdGVyLXNwZWVkeS1yZWNvdmVyeS9hbXAv?oc=5" target="_blank">We wish the Prime Minister a speedy recovery</a>&nbsp;&nbsp;<font color="#6f6f6f">Telegraph.co.uk</font></li><li><a href="https://news.google.com/__i/rss/rd/articles/CBMigAFodHRwczovL3d3dy5pbmRlcGVuZGVudC5jby51ay92b2ljZXMvYm9yaXMtam9obnNvbi1jb3JvbmF2aXJ1cy1pbnRlbnNpdmUtY2FyZS1hZ2UtZG9taW5pYy1yYWFiLWRlcHV0eS1ob3NwaXRhbC1pY3UtYTk0NTEzMDEuaHRtbNIBhAFodHRwczovL3d3dy5pbmRlcGVuZGVudC5jby51ay92b2ljZXMvYm9yaXMtam9obnNvbi1jb3JvbmF2aXJ1cy1pbnRlbnNpdmUtY2FyZS1hZ2UtZG9taW5pYy1yYWFiLWRlcHV0eS1ob3NwaXRhbC1pY3UtYTk0NTEzMDEuaHRtbD9hbXA?oc=5" target="_blank">Now Boris Johnson is in intensive care, this is what Dominic Raab needs to do tonight</a>&nbsp;&nbsp;<font color="#6f6f6f">The Independent</font></li><li><strong><a href="https://news.google.com/stories/CAAqOQgKIjNDQklTSURvSmMzUnZjbmt0TXpZd1NoTUtFUWlSM3FpNWo0QU1FWFJoWVNjZlFLZElLQUFQAQ?oc=5" target="_blank">View Full coverage on Google News</a></strong></li></ol>'


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



def translate_html(html_fragment):
    """
    Translates a HTML fragment to plain text.

    html_fragment: string (ascii or unicode)
    returns: string (ascii)
    """
    txt = ""                 # translated string
    parser_reg=""            # parser register
    parser_state = "TEXT"    # parser state: TEXT, ESCAPE or TAG
    
    for x in html_fragment:  # process each character in html fragment
        parser_reg += x     
        if parser_state == "TEXT":   # in TEXT mode.
            if x == '<':             # does this char start a tag?
                parser_state = "TAG"
            elif x == '&':           # does this char start an escape code?
                parser_state = "ESCAPE"
            else:                    # otherwise, this is normal text
                txt += x             # copy the character as-is to output
                parser_reg = ""      # character handled, erase register
        elif parser_state == "TAG":  # inside an html TAG.
            if x == '>':             # does this char end the tag?
                parser_state = "TEXT"# return to TEXT mode for next character

                tag = parser_reg     # the complete tag is in the register           

                # translate some tags, ignore all others
                if tag[1:-1] == "br" or tag[1:4] == "br ":
                    txt += "\n"
                elif tag == "</table>":
                    txt += "\n"
                elif tag == "<p>":
                    txt += "\n\n"

                parser_reg = ""      # tag handled, erase register
                
        elif parser_state == "ESCAPE": # inside an ESCAPE code
            if x == ';':               # does this char end an escape code?
                parser_state = "TEXT"  # return to TEXT mode for next character

                esc = parser_reg[1:-1] # complete escape code is in register 
                
                if esc in HTML_ESCAPE_DECODE_TABLE:  # try to decode escape code
                    txt += HTML_ESCAPE_DECODE_TABLE[esc]
                else:
                    txt += " "         # unknown escape code -> space
                    
                parser_reg = ""      # code handled, erase register

    if ~isinstance(txt, str):
        txt = unicode_to_ascii(txt)
        
    return txt

if __name__ =='__main__':
    text = translate_html(html_fragment)
    print(text)