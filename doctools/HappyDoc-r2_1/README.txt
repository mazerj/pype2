HappyDoc Documentation Extraction Tool

  HappyDoc is a tool for extracting documentation from Python source
  code.  It differs from other such applications by the fact that it
  uses the parse tree for a module to derive the information used in
  its output, rather that importing the module directly.  This allows
  the user to generate documentation for modules which need special
  context to be imported.


Download

  Download the latest version of
  "HappyDoc":http://sourceforge.net/projects/happydoc/ from
  "SourceForge":http://sourceforge.net .

  Thanks to <A href="http://sourceforge.net"> <IMG
  src="http://sourceforge.net/sflogo.php?group_id=9678" width="88"
  height="31" border="0" alt="SourceForge"></A> for hosting
  HappyDoc development.


Installation

  HappyDoc uses the Distutils package for installation.  Unpack the
  tarball downloaded from SourceForge in a temporary directory.  Then
  run::

    % python ./setup.py install

  to install the package in a central location.  Alternatively,
  HappyDoc can be run directly from its unpacked distribution archive.
  Use this method if you do not have write access to the
  'site-packages' directory for your Python installation.

  For the Impatient

    After installation, the HappyDoc command-line application should
    be in your path.  Simply run 'happydoc' with appropriate
    arguments.  The default behavior for HappyDoc is to read the files
    and directories specified as arguments and generate HTML output to
    the directory './doc'.  *Give it a whirl!*


General Information

  HappyDoc uses the Python parser to extract information from
  '__doc__' strings.  It also examines the signatures of functions and
  methods to include function prototypes in the output.  

  To use HappyDoc, simply run it against your source files or
  directory.  Use the '-h' or '--help' arguments to learn about the
  arguments and options accepted.  See below for more detailed
  directions about configuring your source for documentation purposes.

  Controlling the Output

    HappyDoc uses two different pluggable classes for controlling
    output.  A **formatter** class is responsible for producing the
    syntax of the actual output (e.g. HTML, XML, SGML, or PDF).  A
    **docset** class is responsible for controlling the formatter and
    managing the logical flow of the information (e.g., writing to
    multiple files or a single file, putting class documentation in a
    different file from the module, etc.).  Formatters and DocSets
    should be implemented so that any two can be combined.  It will
    not always be desirable to do this, but it should be possible.

  Documentation not in Doc-strings

    It is not always desirable to put all documentation in '__doc__'
    strings.  Sometimes, notably when working with
    "Zope":http://www.zope.org , special meaning is attached to the
    presence of '__doc__' strings.  For this reason, and to support
    existing code which might not have '__doc__' strings, HappyDoc
    will find and extract documentation in Python comments.  

    Comment documentation can contain all of the same formatting as
    '__doc__' strings.  The preceding comment marker will be stripped
    off and the lines will be assembled and treated as a block of text
    in the same way that the '__doc__' strings are treated.

    To use this feature, it is important to place the comments
    **before** the named object which they describe.  In this example::

      #
      # Class documentation goes here
      #
      class ClassWithNoDocStrings:
         "Using __doc__ strings overrides comment documentation."

         def method1(self, params):
             "This method uses a __doc__ string."
             pass

         #
         # Method2 does not use a __doc__ string.
         #
         def method2(self):
             pass

    The output would include the '__doc__' strings for the class and
    for 'method1'.  It would also make it appear that 'method2' had a
    '__doc__' string with the contents '"Method2 does not use a
    __doc__ string."'


Flexible Behavior

  HappyDoc provides several different abstractions to allow the same
  engine to process different types of inputs and convert them to
  different types of output.

  Docstring Converters

    *How does an author write documentation so that it will be marked
    up and look fancy?* This is a perennial question for
    "Python":http://www.python.org users, and seems to have introduced
    a roadblock into the development of more robust and useful
    documentation tools.  HappyDoc stands firmly on the fence and does
    not attempt to resolve the issue.  

    *Refer to the 'happydoclib.docset' package for more details.*

  Formatters

    Formatters are responsible for tranlating the higher level docset
    concepts into specific structures for an output type.  For
    example, the specific way a descriptive list might be rendered in
    HTML could vary between different HTML formatters.  The API for a
    formatter depends on the docset types which is is meant to
    support.

    *Refer to the 'happydoclib.formatter' package for more details.*


  DocSet types

    The docset, or *documentation set*, defines the structure of the
    collected documentation being generated.  All aspects of the
    structure are left up to the docset.  Whether to use multiple or a
    single file, a file or a database, and what specific metadata to
    include in the output is left up to the docset.  The docset drives
    the documentation generation using controls available from the
    formatter.

    *Refer to the 'happydoclib.docset' package for more details.*

Using HappyDoc

  Command Line Options

    HappyDoc uses standard 'getopt' style command line processing.
    For the complete reference of argument syntax, call the command
    line program with the '-h' or '--help' options.  The specific
    options supported are not documented here since they change over
    time.

  Parser, DocSet and Formatter Parameters

    Many DocSets and Formatters will take parameters.  The Parser also
    accepts global options using this method (see below for another
    way to control the parser).  To pass parameters past the command
    line argument processing of HappyDoc and in to the Parser, DocSet
    or Formatter being used, the variable is passed as an argument
    rather than option (no dashes) to HappyDoc.

    To allow the Parser, DocSets and Formatters to share variable
    namespace, the options passed are prefixed with a value indicating
    whether the variable is for the 'parser_', 'docset_' or
    'formatter_'.

    For example::

      % ./happydoc -d MySources/doc MySources \
		formatter_bgcolor1='#ffccaa'

    Or on Windows::

      > .\happydocwin.py -d MySources\doc MySources \
		formatter_bgcolor1="#ffccaa"

    Use the '--help' command line option to get a complete list of the
    options available for each Parser, DocSets, and Formatter.

  File-specific Parser Configuration Values

    Parameters to the HappyDoc Parser can also be embedded within the
    first comment block of the module.  The parameter values
    recognized and their meanings are listed below.

    To provide file-specific parser configuration settings, any Python
    code can be embedded in the comments of the file.  For example::

      #!/usr/bin/env python
      #
      # HappyDoc:# These variables should be discovered.
      # HappyDoc:TestInt=1
      # HappyDoc:TestString="String"
      # HappyDoc:TestStringModule=string.strip(' this has spaces in front and back ')
      # HappyDoc:url=urlencode({'a':'A', 'b':'B'})
      # HappyDoc:docStringFormat='StructuredText'

    All lines beginning with the pattern "'# HappyDoc:'" will be
    concatenated (separated by newlines) and 'execed'.  The local
    namespace resulting from the execution of the code will be
    examined for variables of interest to the parser.  The incoming
    global namespace for the configuration code will have a few
    pre-populated names for convenience.

    *Refer to the happydoclib.parseinfo module for more details.*

  Input Types

    HappyDoc accepts 3 basic input types for documentation.  

    1. Any **file name** passed will be treated as a Python source file.
       The file will be parsed (but not imported) and the
       documentation text will be extracted from the resulting parse
       tree.

    2. Any **directory** passed will be interpreted to mean to document
       all of the files in that directory, so HappyDoc will recurse
       into the directory to find files.

    3. A **single, regular, text file** can be passed as the "package
       description file."  This file, defaulting to 'README.txt', will
       be interepreted as appropriate and included in the place of a
       '__doc__' string in the generated 'index.html' file.

Examples of HappyDoc Documentation

  Two example output documentation sets are available.

  - **HappyDoc**

    Of course HappyDoc is used to produce its own documentation.  The
    most current version is available on the 
    "HappyDoc home page":http://happydoc.sourceforge.net.

  - **Zope**

    Download a set of "Zope source
    documentation":http://www.zope.org/Documentation/Developer/ZopeSrcDocs
    based on a recent CVS checkout or most stable release of Zope on
    "Zope.org":http://www.zope.org.

    Browse the "Zope CVS Source":Zope-2-CVS-srcdocs documentation on
    the HappyDoc site.

Who else is using HappyDoc?

  - **Biopython** 

    The "Biopython project":http://www.biopython.org uses HappyDoc to
    generate the documentation for their
    "libraries":http://www.biopython.org/wiki/html/BioPython/BiopythonCode.html

  - **Numerical Python** 

    "Numerical Python":http://numpy.sourceforge.net adds a fast,
    compact multidimensional array language facility to Python.

  - **CDAT** 

    "Climate Data Analysis Tool":http://cdat.sourceforge.net is a
    Python-based, easily extendible system for accessing and analyzing
    climate data. It contains a generally useful system for scientific
    graphics.

  - **NOAA SEC**

    The NOAA "Space Environment Center":http://www.sec.noaa.gov/sxi
    group responsible for supporting the effort to forecast solar
    activity having a direct impact on earth-orbiting satellites and
    other earth-based systems.

  - **ZOD**

    The "Zope Online
    Documentation":http://demo.iuveno-net.de/iuveno/Products/ZOnlineDocu
    tools use the HappyDoc parsing engine to extract information about
    source code.

Bugs

  Please use the "bug tracker":http://sourceforge.net/bugs/?group_id=9678 on the
  SourceForge project page for HappyDoc to report bugs and the 
  "feature tracker":http://sourceforge.net/tracker/?group_id=9678&atid=359678
  to request new features.

Support

  There are also "public forums":http://sourceforge.net/forum/?group_id=9678 
  and "mailing lists":http://sourceforge.net/mail/?group_id=9678 available on 
  SourceForge for questions regarding the use of HappyDoc, or plans for its
  future.
