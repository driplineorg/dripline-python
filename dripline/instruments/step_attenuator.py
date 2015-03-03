from __future__ import absolute_import  
##this makes sure python can use stuff from newer versions of python

import logging
import spidev
##here import outside libraries that you will use later

from ..core import Endpoint
##if you needed to import anything from dripline (Spime, Provider, ect) import specific things here  

logger = logging.getLogger(__name__)

__all__= ['StepAttenuator']
##this is what classes are exported when you try to use this file so that they go to the global namespace. Since StepAttenuator is the only class you've made this should be the only name in the list. 

class StepAttenuator(Endpoint):
    def __init__(self, file_name="/tmp/step_atten.txt", **kwargs):
        self.file_name=file_name
        Endpoint.__init__(self, **kwargs)         

    #**kwargs is a library that has arguments. If your class is given a name that it doesn't have a value/function for it will pass it to kwargs, which will pass it along to the parent class, which will do the same thing. 
    #If you haven't came up with something for your function to do, pass it so that it doesn't do anything but you can still run file.
   #Before you had to be in the instruments directory in order for python to see that the file you wanted to open existed. By creating an argument named that gives a default location for the file you can work around that so other people don't need to be in instruments to run the code. 
   
    def on_get(self):
        f= open(self.file_name, "r+")
        lines= f.readlines()
        last_line= lines[-1]
        logger.debug("last value was: {}".format(last_line))
        f.close()
        return last_line

##This opens up the temp file, which can be called/put where the user wants, and recalls the last line of the file

    def on_set(self, value):      
        self.value=value
        spi= spidev.SpiDev()
        spi.open(0, 0)
        logger.debug('value[type] is: {}[{}]'.format(value,type(value)))
        spi.xfer([int(value)])
        spi.close()           
        f= open(self.file_name, "a")
        string=str(value)
        f.write(string + '\n')
        f.close()
        return string

##First creates spi object and then opens a spi port 0, device 0. Xfer performs a SPI transaction. So return the value that you want to set the attenuation as. Without the SPI lines the actual attenuation will not change but your new values will be written in a file--that doens't actually do anything useful.  
##This sets the new value for the SA but rewrites the file and deletes the old content. This is fine for now but it something to fix in the future. 
