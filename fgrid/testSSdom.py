r"""testSSdom.py tests Server-side DOM
Usage:   ./testSSdom.py
Sample:  ./testSSdom.py
see:    
  1. IBID == [YATL helpers - Server-side DOM](https://py4web.com/_documentation/static/en/chapter-10.html#server-side-dom)
    - in IBID page, find "by specifying a replace argument"
      - ` a = DIV(DIV(SPAN('x', _class='abc'), DIV(SPAN('y', _class='abc'), SPAN('z', _class='abc')))) `
      2. this was posted in [YATL helpers - Server-side DOM -- AttributeError: 'XML' object has no attribute 'name'](https://groups.google.com/g/py4web/c/LlgGeNOhYOQ)

"""

import os
from yatl.helpers import *  

def testSSdom():
    # example at find  "by specifying a replace argument"  on  IBID == [YATL helpers - Server-side DOM](https://py4web.com/_documentation/static/en/chapter-10.html#server-side-dom)

    a = DIV(DIV(SPAN('x', _class='abc'), DIV(SPAN('y', _class='abc'), SPAN('z', _class='abc'))))
    print('type(a): %s'%(type(a)))
    print('      a: %s'%(a)) #     a: <div><div><span class="abc">x</span><div><span class="abc">y</span><span class="abc">z</span></div></div></div>
    print('a.xml(): %s'%(a.xml()))
    a_str = a.xml()
    print('  a_str: %s'%(a_str)) # a_str: <div><div><span class="abc">x</span><div><span class="abc">y</span><span class="abc">z</span></div></div></div>


    # find that WILL work
    print('\n\nfind that WILL work')
    for e in a.find('span.abc'): print( "a.find('span.abc'): %s"%(e.xml()) )  #  searches a  for    'span.abc'    no substring 'name' here


    # find that USED TO THROW ERROR   - STILL DOES NOT work (no prints)
    print('\n\nfind that USED TO THROW ERROR   - STILL DOES NOT work (no find prints)')
    a_xml = XML(a_str)
    print('beforeErrorTest - type(a_xml): %s'%( type(a_xml)  ))
    print('beforeErrorTest - a_xml.xml(): %s'%( a_xml.xml()  ))

    for e in a_xml.find('span.abc'): print( "a_xml.find('span.abc'): %s"%(e.xml()) )  

    print('afterErrorTest -  a.xml() == a_xml.xml(): %s'%(a.xml() == a_xml.xml()))

   
def main():
    print('\n')
    testSSdom()
    print('\n')


if __name__ == '__main__':
    main()
