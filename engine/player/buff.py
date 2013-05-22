'''
Created on 16.5.2013

@author: marko

'''

def setBufferSize(iStreamed, size):
    """
    set buffer size in (B)
    """
    if iStreamed:
        iStreamed.setBufferSize(size)
    

def getBufferInfo(iStreamed):
    """
    @return:{ percentage: buffer percent,
              avg_in_rate: average input rate (B),
              avg_out_rate: average output rate (B),
              space: buffer space (s),
              size: buffer size (B),
              downloading: bool,
              download_path: download path,
              download_percent: download percent (B)
            }
    """
                   
    
    bufferDict = {'percentage':0,
                  'space':0,
                  'size':0,
                  'avg_in_rate':0,
                  'avg_out_rate':0,
                  # servicemp4 download stuff
                  'downloading':False,
                  'download_path':'',
                  'downloa_percent':0
                  }
    
    if iStreamed:
        bufferInfo = iStreamed.getBufferCharge()
        bufferDict['percentage'] = bufferInfo[0]
        bufferDict['avg_in_rate'] = bufferInfo[1]
        bufferDict['avg_out_rate'] = bufferInfo[2]
        bufferDict['space'] = bufferInfo[3]
        bufferDict['size'] = bufferInfo[4]
        
        try:
            # servicemp4 download
            bufferDict['downloading'] = bufferInfo[5]
            bufferDict['download_path'] = bufferInfo[6]
            bufferDict['download_percent'] = bufferInfo[7]
        except IndexError:
            pass
    return bufferDict
