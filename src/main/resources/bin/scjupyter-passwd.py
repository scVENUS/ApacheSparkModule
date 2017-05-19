#!/usr/bin/env python

# Copyright (C) 2017 by science + computing ag
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import getpass
import hashlib
import random
import sys

salt_len = 12
algorithm = 'sha1'

if __name__ == '__main__':
    password = None
    pw1 = getpass.getpass('Enter password: ')
    pw2 = getpass.getpass('Verify password: ')
    if pw1 != pw2:
        print >> sys.stderr, 'Passwords do not match.'
        sys.exit(1)
    else:
        password = pw1

    hash = hashlib.new(algorithm)
    salt = ('%0' + str(salt_len) + 'x') % random.getrandbits(4 * salt_len)
    hash.update(password.encode('utf-8', "replace") + salt)
    print ':'.join((algorithm, salt, hash.hexdigest()))
