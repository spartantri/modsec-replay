#!/usr/bin/env python 
#
#
# This script parses the audit log
# Needs SecAuditLogParts with ABCDEF, Native or JSON format
# JSON format support by spartantri

import os, hashlib, fnmatch

# Recursive file list
def findFiles(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def isValidOffset(filename,offset=0):
    """Check if the log file offset is valid
    
    Args:
        filename: The complete path of the file.
    
    Returns:
        Maximum offset (line count) if valid. Zero if invalid.
    """
    num_lines = sum(1 for line in open(filename))
    if offset<=num_lines:
        return num_lines
    else:
        return 0

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
            if li.startswith('{"transaction":{"time":"'):
                validCount = 3
            elif li.startswith("--") and li.endswith("-A--"):
                validCount += 1
            elif li.startswith("--") and li.endswith("-B--"):
                validCount += 1
            elif li.startswith("--") and li.endswith("-E--"):
                validCount += 1
    return validCount >= 3

def requestHash(filename):
    return hashlib.md5(os.path.basename(filename)).hexdigest()

def getAuditPart(filename,part,offset=0):
    captureFlag = jsonFlag = False 
    lineNumber = 0
    outBuffer = ""
    if os.path.isfile(filename) and isValidFile(filename):
        with open(filename, "r") as f:
            for line in f.read().split('\n'):
                if offset>0:
                    if lineNumber<offset:
                        lineNumber+=1
                        continue
                li = line.strip()
                if li.startswith('{"transaction":{"time":"'):
                    import json
                    if part == "LOG":
                        return str(json.loads(li)['request']['request_line'])
                    elif part == "REQUEST-HEADER":
                        for header in json.loads(li)["request"]["headers"].keys():
                            outBuffer=''.join([outBuffer, header, ":", json.loads(li)["request"]["headers"][header], "\n"])
                        return outBuffer
                    elif part == "REQUEST-BODY":
                        try:
                            outBuffer=json.loads(li)["request"]["body"][0]
                        except:
                            outBuffer=""
                        return outBuffer
                    elif part == "RESPONSE-HEADER":
                        for header in json.loads(li)["response"]["headers"].keys():
                            outBuffer=''.join([outBuffer, header, ":", json.loads(li)["response"]["headers"][header], "\n"])
                        return outBuffer
                    elif part == "RESPONSE-BODY":
                        try:
                            outBuffer=json.loads(li)["response"]["body"][0]
                        except:
                            outBuffer=""
                        return outBuffer
                    elif part == "UNIQUE-ID":
                        return str(json.loads(li)['transaction']['transaction_id'])
                elif li.startswith("--") and li.endswith("-A--"):
                    if part == "LOG" or part == "UNIQUE-ID":
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
                elif li.startswith("--") and li.endswith("--") and len(li) == 14:
                    captureFlag = False
                if captureFlag:
                    if lineNumber > 0:
                        outBuffer = outBuffer + line + "\n"
                        if part == "UNIQUE-ID":
                            return line.split("]")[1].strip().split(" ")[0]
                    lineNumber = lineNumber + 1
        return outBuffer
    return None
