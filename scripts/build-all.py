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

tmp = Path('tmp')
tmp.mkdir(exist_ok=True)

import shutil
import os
import subprocess
import logging
import re

logging.basicConfig(level=logging.INFO)

# print(get_associations())
for tc in testcases:
    logging.debug('Test case %s begin', tc['@id'])

    # We will build the tc in this dir
    build_dir = Path(tmp / tc['@id'])
    build_dir.mkdir(exist_ok=True)
    
    # Copy all files to this directory
    cs = []
    main = None
    for fnode in tc['file']:
        srcfile = Path(fnode['@path'])
        assert(srcfile.exists())
        dstfile = build_dir / srcfile
        if srcfile.suffix == '.h' or 'main' in srcfile.name:
            os.makedirs(dstfile.parent, exist_ok=True)
            shutil.copy(srcfile, build_dir / srcfile)
            if 'main' in srcfile.name:
                main = srcfile
        else:
            cs.append(srcfile)
    assert(main is not None)
    build_cwd = build_dir / main.parent
    for srcfile in cs:
        try:
            shutil.copy(srcfile, build_cwd)
        except SameFileError:
            pass

    # Build the tc
    instruction = tc['@instruction']
    args = instruction.split()
    # args += ['-o', re.sub(r'(.*)_main\.c', r'\1', main.name)]
    logging.debug('Build command: %s', args)
    process = subprocess.Popen(args=args, cwd=build_cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    out_str = out.decode('utf-8').strip()
    if process.returncode != 0:
        logging.error('Could not build testcase: %s. Build output:\n%s', tc['@id'], out_str)
        continue
    else:
        logging.debug('Build output:\n%s', out_str)
    
    logging.debug('Test case %s built', tc['@id'])
