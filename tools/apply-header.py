#!/usr/bin/env python
#####################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
#####################################################################

import os
import os.path
import sys


def apply_header(source_file, header_file):
  source = read_file(source_file)
  header = header_map[header_file]
  if source.find(header) < 0:
    f = open(source_file, 'w')
    try:
      f.write(header)
      f.write(source)
    finally:
      f.close()


def read_file(file):
  f = open(file, 'r')
  try:
    return ''.join(f.readlines())
  finally:
    f.close()

type_map = {
  'py': 'header-script.txt',
  'js': 'header-c.txt',
  'css': 'header-c.txt',
}

current_dir = os.getcwd()
header_dir = current_dir + os.sep + 'tools'
if not os.path.exists(header_dir):
  print 'Cannot find tools directory. Are you executing this script from the project root directory?'
  sys.exit(1)

header_map = {}
for hfile in type_map.values():
  header_map[hfile] = read_file(header_dir + os.sep + hfile)

for (path, dirs, names) in os.walk(os.getcwd()):
  for name in names:
    n = name.find('.')
    ext = name[n+1:]
    if ext in type_map:
      apply_header(path + os.sep + name, type_map[ext])
