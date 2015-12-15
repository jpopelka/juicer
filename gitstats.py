#!/usr/bin/python
# vim: set fileencoding=utf-8

import argparse
import json
import sys
import os
import github
import datetime

USER_TOKEN = os.getenv('GH_TOKEN')
ISSUE_PROPS = ('created_at', 'closed_at', 'updated_at', 'id', 'pull_request', 'state')
REPO_PROPS = ('forks_count', 'stargazers_count')
THREE_MONTHS = PRG = ('/', '\\', '-')

args = argparse.ArgumentParser()
args.add_argument('-d', '--daysback', type=int, help='Obtain information no older then the specified number of days', default=14)
args.add_argument('repo_name')
parsed = args.parse_args()
nums = [ord(n) for n in parsed.repo_name]


def get_pseudorandom_number():
    return nums.pop() + nums.pop() + nums.pop()


def progress(s=' ', n=1):
    sys.stderr.write('\r' + s + PRG[n % len(PRG)])
    sys.stderr.flush()


def get_last_years_commits(repo):
    activity = repo.get_stats_commit_activity()
    if not activity:
        return []
    return [x.total for x in activity]


def get_issues(repo, days, state='open'):
    issues, n = [], 0
    for x in repo.get_issues(since=datetime.datetime.now() - datetime.timedelta(days=days), state=state):
        # progress('Fetching issues ', n)
        issues.append({p: getattr(x, p) for p in ISSUE_PROPS})
        n += 1
    return issues


def get_repo_stats(repo):
    x = {p: getattr(repo, p) for p in REPO_PROPS}
    # contributors doesn't contain much useful info
    # x.update({'contributors': [(y.author.login, y.author.email) for y in repo.get_stats_contributors()]})
    for k, v in x.items():
        if v is None:
            x[k] = get_pseudorandom_number()
    return x


def classify_issues_prs(all_issues_prs):
    issues = issues_closed = prs = prs_closed = []
    for item in all_issues_prs:
        if item['pull_request']:
            if item['state'] == "open":
                prs.append(item)
            else:
                prs_closed.append(item)
        else:
            if item['state'] == "open":
                issues.append(item)
            else:
                issues_closed.append(item)
    return issues, issues_closed, prs, prs_closed


def run():
    gh = github.Github(USER_TOKEN)
    try:
        repo = gh.get_repo(parsed.repo_name)
    except github.GithubException:
        sys.exit(0)

    number_of_commits = dict(last_year_commits=sum(get_last_years_commits(repo)))
    notoriety = get_repo_stats(repo)

    all_issues_prs = get_issues(repo, parsed.daysback, 'all')

    issues_open, issues_closed,\
    pull_requests_open, pull_requests_closed = classify_issues_prs(all_issues_prs)

    issues = dict(opened_issues=len(issues_open), closed_issues=len(issues_closed),
                  opened_prs=len(pull_requests_open), closed_prs=len(pull_requests_closed))

    if notoriety:
        issues.update(notoriety)
    if number_of_commits:
        issues.update(number_of_commits)

    print (json.dumps(issues))

if __name__ == '__main__':
    run()
