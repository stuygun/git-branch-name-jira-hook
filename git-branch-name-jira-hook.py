#!/usr/bin/env python

########################################################################################################################
# Git Hook which extract the JIRA Ticket ID from the branch name and
# check against Jira.
# Branch format is :
# ^(feature|bugfix|improvement|library|prerelease|release|hotfix)\/([a-zA-Z0-9-]+?)(\_)([a-zA-Z0-9._-]+?)$
# Example:
#   feature/PRJ-123_Some_Definition -> correct
#   feature/PRJ-321_Some_Definition -> correct however if PRJ-321 status us done than it will give error
#   bug/PRJ-123_Some_Definition -> incorrect as it should start with bug which is not in the regex
#   feature/SOME_TEXT -> incorrect as SOME is not a correct Jira Ticket ID format
########################################################################################################################

from jira import JIRA
import subprocess
import logging
import os
import sys
import re

filename = os.path.basename(sys.argv[0])
loglevel = logging.ERROR


def main():
    global filename, loglevel
    logging.basicConfig(level=loglevel, format=filename + ":%(levelname)s: %(message)s")
    return_code = handle_commit_msg()
    logging.debug('return_code', return_code);
    return return_code


def handle_commit_msg():
    jira = jira_start_session()
    branch_name = git_get_curr_branch_name()
    logging.debug('branch_name', branch_name)
    issue_key = get_issue_key_from_branch(branch_name)
    if issue_key is not -1:
        logging.debug('issue_key', issue_key)
        return jira_find_issue(issue_key, jira)
    return -1


def get_issue_key_from_branch(branch_name):
    issue_search = re.search(
        '^(feature|bugfix|improvement|library|prerelease|release|hotfix)\/([a-zA-Z0-9-]+?)(\_)([a-zA-Z0-9._-]+?)$',
        branch_name, re.IGNORECASE)

    if issue_search:
        return issue_search.group(2)
    logging.error("Issue could not be extracted from the branch name. Branch name format is \n"
                  "^(feature|bugfix|improvement|library|prerelease|release|hotfix)\/([a-zA-Z0-9-]+?)(\_)(["
                  "a-zA-Z0-9._-]+?)$")
    return -1


# JIRA FUNCTIONS
def jira_start_session():
    jira_url = str(get_jira_url())
    logging.debug('jira_url', jira_url)
    jira_user = str(get_jira_user())
    logging.debug('jira_user', jira_user)
    jira_token = str(get_jira_token())
    logging.debug('jira_token', jira_token)

    options = {'server': jira_url}
    jira = JIRA(options, basic_auth=(jira_user, jira_token))

    return jira


def jira_find_issue(issuekey, jira):
    try:
        print
        issuekey
        issue = jira.issue(issuekey)
        logging.debug("Found issue '%s' in Jira: (%s) status: %s",
                      issuekey, issue.fields.summary, issue.fields.status)

        # Check the status it should not be DONE
        status = issue.fields.status
        if "done" == str(status).lower():
            logging.error("The issue (%s) is already resolved.", issuekey)
            return -1

        return 0

    except KeyboardInterrupt:
        logging.info("... interrupted")

    except Exception as e:
        logging.error("No such issue '%s' in Jira", issuekey)
        logging.debug(e)
        return -3


# GIT FUNCTIONS
def get_jira_token():
    jira_token = git_config_get("jira.token")
    if jira_token is None or jira_token == "":
        logging.error("Jira token is not set. Please use 'git config jira.token <actual-jira-token> to set it'")
        return None

    return jira_token.rstrip()


def get_jira_user():
    jira_user = git_config_get("jira.user")
    if jira_user is None or jira_user == "":
        logging.error("Jira user is not set. Please use 'git config jira.user <actual-jira-user> to set it'")
        return None

    return jira_user.rstrip()


def get_jira_url():
    jira_url = git_config_get("jira.url")
    if jira_url is None or jira_url == "":
        logging.error("Jira URL is not set. Please use 'git config jira.url <actual-jira-url> to set it'")
        return None

    return jira_url.rstrip()


def git_config_get(name):
    return subprocess.run(['git', 'config', name], stdout=subprocess.PIPE).stdout.decode('utf-8')


def git_get_curr_branch_name():
    return subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')


if __name__ == "__main__":
    main()
