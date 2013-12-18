try:
    print "Key Store loading..."
    from keyList import keys
except ImportError:
    import os
    if not os.path.exists("keyList.py"):
        print "Key Store Creation..."
        try:
            f = open("keyList.py", 'w')
            f.write("#"+os.linesep)
            f.write("#"+os.linesep)
            f.write("# OFFLINE key set"+os.linesep)
            f.write("#"+os.linesep)
            f.write("keys = {}"+os.linesep)
            f.write(os.linesep)
            f.close()
            
        except IOError as ioe:
            print "failed to create the key store : "+str(ioe)
            exit()
        
        keys = {}
