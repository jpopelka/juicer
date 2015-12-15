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
        issues.append({p: getattr(x, p, '???') for p in ISSUE_PROPS})
        n += 1
    return issues


def get_repo_stats(repo):
    d = {p: getattr(repo, p, '???') for p in REPO_PROPS}
    # contributors doesn't contain much useful info
    # contributors = repo.get_stats_contributors()
    # if contributors:
    #     d['contributors'] = [(y.author.login, y.author.email) for y in contributors]
    return d


def classify_issues_prs(all_issues_prs):
    ret = {'issues': {'open': [], 'closed': []},
           'pull_requests': {'open': [], 'closed': []}}
    for item in all_issues_prs:
        itype = 'pull_requests' if item['pull_request'] else 'issues'
        state = item['state']
        ret[itype][state].append(item)
    return ret


def run():
    gh = github.Github(USER_TOKEN)
    try:
        repo = gh.get_repo(parsed.repo_name)
    except github.GithubException:
        sys.exit(0)

    all_issues_prs = get_issues(repo, parsed.daysback, 'all')
    classified_issues_prs = classify_issues_prs(all_issues_prs)
    n_issues_open = len(classified_issues_prs['issues']['open'])
    n_issues_closed = len(classified_issues_prs['issues']['closed'])
    n_pull_requests_open = len(classified_issues_prs['pull_requests']['open'])
    n_pull_requests_closed = len(classified_issues_prs['pull_requests']['closed'])
    issues = {'issues': {'open': n_issues_open, 'closed': n_issues_closed},
              'pull_requests': {'open': n_pull_requests_open, 'closed': n_pull_requests_closed}}

    notoriety = get_repo_stats(repo)
    if notoriety:
        issues.update(notoriety)
    last_year_commits = get_last_years_commits(repo)
    commits = {'last_year_commits': {'sum': sum(last_year_commits), 'weekly': last_year_commits}}
    issues.update(commits)

    print (json.dumps(issues))

if __name__ == '__main__':
    run()
