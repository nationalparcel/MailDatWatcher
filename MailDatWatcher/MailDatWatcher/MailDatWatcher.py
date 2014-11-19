import os
import sys
import zipfile
import subprocess
import shutil
import time

#strings
pathToFtp = "F:\\mailDats"
pathToDatFolder = "C:\\DATData"

def unZipFile (filePath):
    try:
        #zfile = zipfile.ZipFile(filePath)
        fileToUnzip = open(filePath, 'rb')
        zfile = zipfile.ZipFile(fileToUnzip)
        for name in zfile.namelist():
            if ( name.find(".csm") != -1 or name.find(".hdr") != -1):
                zfile.extract(name, pathToDatFolder)

        fileToUnzip.close()
        return
    except Exception, err:
        print str(err)
        print "zip file done"

def runCSMToFMS ():
    for path, subdir, files in os.walk (pathToDatFolder):
        for filename in files:
            if (filename.find(".hdr") != -1):
                file = open(path + "\\" + filename)
                hdrContents = file.read()
                if hdrContents.find("14-1") != -1:
                    exedir = "C:\\CustomApps\\MailDirectCSMToFMS\\bin\\FourteenOne\\CSMToFMS.exe"
                    output = subprocess.Popen([exedir], stdout = subprocess.PIPE)
                    resualts = output.communicate()[0]
                    print resualts
                    output.terminate()
                elif hdrContents.find("14-2") != -1:
                    exedir = "C:\\CustomApps\\MailDirectCSMToFMS\\bin\\FourteenTwo\\CSMToFMS.exe"
                    output = subprocess.Popen([exedir], stdout = subprocess.PIPE)
                    resualts = output.communicate()[0]
                    print resualts
                    output.terminate()
                else:
                    resualts = "error"

                if resualts.find("Finished") == -1:
                    resualts = "error"

                print resualts
                file.close()
                return resualts

for path, subdir, files in os.walk(pathToFtp):
    for filename in files:
        if filename.find(".zip") != -1 and path.find("archive") == -1:
            pathToZipFile = path + "\\" + filename
            unZipFile( pathToZipFile )
            resaults = runCSMToFMS()
            try:
                if resaults != "error":
                    for p, s, cleanUpFiles in os.walk( pathToDatFolder ):
                        for datFileName in cleanUpFiles:
                            src = pathToDatFolder + "\\" + datFileName
                            print src
                            dest = path + "\\archive\\" + datFileName
                            print dest
                            shutil.move(src, dest)
                else:
                    for p, s, cleanUpFiles in os.walk( pathToDatFolder ):
                        for datFileName in cleanUpFiles:
                            src = pathToDatFolder + "\\" + datFileName
                            print src
                            dest = pathToFtp + "\\Errors\\" + datFileName
                            print dest
                            shutil.move(src, dest)
                            with open("C:\\Users\\administrator.NPLATL\\Desktop\\Server Side Scripts\\DatWatcher\\Logs\\errorLog.txt", "a") as logFile:
                                logFile.write("*****\n" + str(time.strftime("%d/%m/%Y")) + "\n" + "Problem with CMStoFMS Program - " +datFileName+ "\n \n")

                    
                os.remove(pathToZipFile)
            except Exception, err:
                print str(err)
                with open("C:\\Users\\administrator.NPLATL\\Desktop\\Server Side Scripts\\DatWatcher\\Logs\\errorLog.txt", "a") as logFile:
                    logFile.write("*****\n" + str(time.strftime("%d/%m/%Y")) + "\n" + str(err) + "\n \n")
                