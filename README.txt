pynmr
=====

pyNMR is a set of python modules to parse, process, and analyze NMR data.

There are some fragments of a graphical user interface but at this point pyNMR is best used together with Jupyter Lab.

Currently supported NMR formats are Bruker TopSpin and RS2D.

There is some code for parsing files from Tecmag NTNMR, Magritek, and Varian under pynmr/model/parser, but at this point these formats are not
officially supported.


Installation
------------

pynmr is available at pip. It may be installed
with

::

	pip install pynmr



Usage
------------
To import a Bruker dataset instantiate an nmr Data  object:

..code:: python

	 import pynmr
	 path = "pathToTopSpin/"
	 
	 import pynmr.model.parser.topSpin as T
	 import pynmr.model.processor as P
	 import pynmr.model.operations as O
	 
	 import matplotlib.pyplot as plt
	 import numpy as np
	 
	 data = T.TopSpin("./data/bruker/dnp_210316_1_solids/1/")
	 
	 Processor = P.Processor([O.LeftShift(21),
                         O.LineBroadening(0.2),
                         O.FourierTransform(),
                         O.Phase0D(190)])
	 Processor.runStack(data)
	 


Internal Notes
-------------
To install this package locally and install for development, use this command

>>> pip install -e ./

More info available here: https://packaging.python.org/tutorials/installing-packages/


MIT License
-----------

Copyright (c) 2022 Benno Meier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
