#!/usr/bin/python 
#
#
# This script parses the audit log
# Needs SecAuditLogParts with ABCDEF
#

import os, hashlib, fnmatch

# Recursive file list
def findFiles(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def isValidFile(filename):
    """Check if a audit file is a valid and contains all needed sections (ABE)

    Args:
        filename: The complete path of the file.

    Returns:
        The return value. True for success, False otherwise.
    """
    validCount = 0
    with open(filename, "r") as f:
        for line in f.readlines():
            li = line.strip()
            if li.startswith("--") and li.endswith("-A--"):
                validCount = validCount+1
            elif li.startswith("--") and li.endswith("-B--"):
                validCount = validCount+1
            elif li.startswith("--") and li.endswith("-E--"):
                validCount = validCount+1
    return validCount >= 3

def requestHash(filename):
    return hashlib.md5(os.path.basename(filename)).hexdigest()

def getAuditPart(filename,part):
    captureFlag = False 
    lineNumber = 0
    outBuffer = ""
    if os.path.isfile(filename) and isValidFile(filename):
        with open(filename, "r") as f:
            for line in f.readlines():
                li = line.strip()
                if li.startswith("--") and li.endswith("-A--"):
                    if part == "LOG":
                        captureFlag = True
                    else:
                        captureFlag = False

                elif li.startswith("--") and li.endswith("-B--"):
                    if part == "REQUEST-HEADER":
                        captureFlag = True
                    else:
                        captureFlag = False

                elif li.startswith("--") and li.endswith("-C--"):
                    if part == "REQUEST-BODY":
                        captureFlag = True
                    else:
                        captureFlag = False
                elif li.startswith("--") and li.endswith("-F--"):
                    if part == "RESPONSE-HEADER":
                        captureFlag = True
                    else:
                        captureFlag = False
                elif li.startswith("--") and li.endswith("-E--"):
                    if part == "RESPONSE-BODY":
                        captureFlag = True
                    else:
                        captureFlag = False
        
                if captureFlag:
                    if lineNumber > 0:
                        outBuffer = outBuffer + line
                    lineNumber = lineNumber + 1
        return outBuffer
    return None