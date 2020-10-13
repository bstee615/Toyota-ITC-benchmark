from shutil import SameFileError
import xmltodict
from pathlib import Path

with Path('manifest-104-sNLWhj.xml').open() as srcfile:
    text = srcfile.read()

root = xmltodict.parse(text)
testcases = root['container']['testcase']

def get_associations(tcs):
    """Return a dict of all the pairs of testcases"""
    
    associations = {}
    for tc in tcs:
        assert(tc['association']['@type'] == 'pair')
        for atc in tcs:
            if atc['@id'] == tc['association']['@testcaseid']:
                associations[tc['@id']] = atc['@id']
    return associations
