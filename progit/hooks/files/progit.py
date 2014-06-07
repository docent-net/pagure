#! /usr/bin/env python2


"""Progit specific hook to add comment on issues if the commits fixes or
relates to an issue.
"""

import re
import sys
import subprocess


FIXES = [
    re.compile('fixe[sd]?:? #(\d+)', re.I),
    re.compile('fixe[sd]?:? https?://.*/(\w+)/issue/(\d+)', re.I),
]

RELATES = [
    re.compile('relate[sd]?:? #(\d+)', re.I),
    re.compile('relate[sd]?:? https?://.*/(\w+)/issue/(\d+)', re.I),
]

def read_git_output(args, input=None, keepends=False, **kw):
    """Read the output of a Git command."""

    return read_output(['git'] + args, input=input, keepends=keepends, **kw)


def read_git_lines(args, keepends=False, **kw):
    """Return the lines output by Git command.

    Return as single lines, with newlines stripped off."""

    return read_git_output(args, keepends=True, **kw).splitlines(keepends)


def read_output(cmd, input=None, keepends=False, **kw):
    if input:
        stdin = subprocess.PIPE
    else:
        stdin = None
    p = subprocess.Popen(
        cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw
        )
    (out, err) = p.communicate(input)
    retcode = p.wait()
    if retcode:
        print 'ERROR: %s =-- %s' % (cmd, retcode)
    if not keepends:
        out = out.rstrip('\n\r')
    return out


def generate_revision_change_log(new_commits_list):

    print 'Detailed log of new commits:\n\n'
    for line in read_git_lines(
            ['log', '--no-walk']
            + new_commits_list
            + ['--'],
            keepends=False,
        ):
        print '*', line
        for motif in FIXES:
            if motif.match(line):
                print 'fixes', motif.groups()
        for motif in RELATES:
            if motif.match(line):
                print 'relates to', motif.groups()


def get_commits_id(fromrev, torev):
    ''' Retrieve the list commit between two revisions and return the list
    of their identifier.
    '''
    cmd = ['rev-list', '%s...%s' %(torev, fromrev)]
    return read_git_lines(cmd)


def run_as_post_receive_hook():
    changes = []
    for line in sys.stdin:
        print line
        (oldrev, newrev, refname) = line.strip().split(' ', 2)

        print '  -- Old rev'
        print oldrev
        print '  -- New rev'
        print newrev
        print '  -- Ref name'
        print refname

        generate_revision_change_log(get_commits_id(oldrev, newrev))


def main(args):
        run_as_post_receive_hook()


if __name__ == '__main__':
    main(sys.argv[1:])
