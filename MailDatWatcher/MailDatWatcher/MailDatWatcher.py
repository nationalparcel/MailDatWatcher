import os
import sys
import zipfile
import subprocess
import shutil
import time
import smtplib

def sendEmail(message, subject, to):
    try:
        sender = 'networkalerts@nationalparcel.com'
        msg = ("From: DatFileError@nationalparcel.com \n"
                   "To: smccoy@nationalparcel.com; dgriffin@nationalparcel.com \n"
                   "Subject: " + subject + "\n"
                   "\n"
                   + message)
        s = smtplib.SMTP('smtp.nationalparcel.com')
        s.login("networkalerts@nationalparcel.com", "2Simplex")
        s.sendmail(sender, to, msg)
    except Exception, err:
        print str(err)
    finally:
        s.quit()

def checkDupUpload(path, fileName):
    jobName = fileName.lower().replace(".zip", "")
    pathOnly = path.replace(fileName, "")
    isThereADup = False
    for p, s, files in os.walk(pathOnly + "//archive"):
        for file in files:
            file = file.lower().replace(".csm", "")
            file = file.lower().replace(".hdr", "")
            if jobName == file:
                isThereADup = True
                break

    return isThereADup

def unZipFile (filePath):
    try:
        fileToUnzip = open(filePath, 'rb')
        zfile = zipfile.ZipFile(fileToUnzip)
        for name in zfile.namelist():
            if ( name.lower().find(".csm") != -1 or name.lower().find(".hdr") != -1):
                zfile.extract(name, pathToDatFolder)

        fileToUnzip.close()
        return
    except Exception, err:
        print str(err)
        writeToLog("Zip file error " + str(err) + "-" + filePath)
        sendEmail("Zip file error - " + str(err), "Zip File Error" + "-" + filePath, ["smccoy@nationalparcel.com", "dgriffin@nationalparcel.com"])

def runCSMToFMS ():
    try:
        for path, subdir, files in os.walk (pathToDatFolder):
            for filename in files:
                if (filename.find(".hdr") != -1):
                    file = open(path + "\\" + filename)
                    hdrContents = file.read()
                    if hdrContents.find("14-1") != -1:
                        output = subprocess.Popen(["C:\\CustomApps\\MailDirectCSMToFMS\\bin\\ForteenOne\\CSMToFMS.exe"], stdout = subprocess.PIPE)
                        resualts = output.communicate()[0]
                        print resualts
                        output.terminate()
                    elif hdrContents.find("14-2") != -1:
                        output = subprocess.Popen(["C:\\CustomApps\\MailDirectCSMToFMS\\bin\\FourteenTwo\\CSMToFMS.exe"], stdout = subprocess.PIPE)
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

    except Exception, err:
        print str(err)
        writeToLog(str(err))

def writeToLog(message):
    logFileLoc = "C:\\Users\\administrator.NPLATL\\Desktop\\Server Side Scripts\\DatWatcher\\Logs\\errorLog.txt"
    #logFileLoc = "C:\\Users\\Shawn\\Desktop\\Server Side Scripts\\DatWatcher\\Logs\\errorLog.txt"
    currentDT = str(time.asctime(time.localtime(time.time())))
    with open(logFileLoc, "a") as logFile:
        logFile.write("*****\n" + currentDT + " - " + message + "\n\n")

def moveCMSFiles (archOrError, pathDatFolder, clientPath):
    moveToFolder = "\\archive\\"
    for p, s, cleanUpFiles in os.walk(pathDatFolder):
        for datFileName in cleanUpFiles:
            if archOrError == "e":
                moveToFolder = "\\Errors\\"
                writeToLog("Problem with CMStoFMS Program" + datFileName)
                sendEmail("Problem with CMStoFMS Program " + datFileName, "CMStoFMS Error", errorEmails)

            src = pathDatFolder + "\\" + datFileName
            dest = clientPath + moveToFolder + datFileName
            shutil.move(src, dest)

def checkForFileLocks (path):
    if os.path.exists(path):
        try:
            os.rename(path, path + "_")
            os.rename(path + "_", path)
            return False
        except OSError as err:
            writeToLog("Access to " + path + " is locked. Waiting till next run")
            return True

#####################################################################################################################################

errorEmails = ["smccoy@nationalparcel.com", "dgriffin@nationalparcel.com"]
pathToFtp = "F:\\mailDats"
pathToDatFolder = "C:\\DATData"

try:
    for path, subdir, files in os.walk(pathToFtp):
        for filename in files:
            if filename.find(".zip") != -1 and path.find("archive") == -1 and path.lower().find("errors") == -1:
                pathToZipFile = path + "\\" + filename
                isFileLocked = checkForFileLocks(pathToZipFile)
                if isFileLocked == False:
                    isThereADup = checkDupUpload(pathToZipFile, filename)
                    if isThereADup == True:
                        sendEmail(filename + " is already uploaded", "Dup Upload Detected", ["smccoy@nationalparcel.com", "dgriffin@nationalparcel.com"])
                        writeToLog(filename + " is already uploaded")
                        shutil.move(pathToZipFile, pathToFtp + "\\Errors\\" + filename)
                    else:
                        unZipFile( pathToZipFile )
                        resaults = runCSMToFMS()
                        if resaults != "error":
                            moveCMSFiles("a", pathToDatFolder, path)
                        else:
                            moveCMSFiles("e", pathToDatFolder, pathToFtp)
                    
                        os.remove(pathToZipFile)
                        time.sleep(20)

except Exception, err:
    print str(err)
    writeToLog(str(err))
    sendEmail("Unhandled Exception - " + str(err), "Unhandled Exception", errorEmails)                