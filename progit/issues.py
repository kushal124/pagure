#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import flask
import os
from math import ceil

import pygit2
from sqlalchemy.exc import SQLAlchemyError
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers.text import DiffLexer
from pygments.formatters import HtmlFormatter


import progit.doc_utils
import progit.lib
import progit.forms
from progit import APP, SESSION, LOG, __get_file_in_tree, cla_required


## URLs

@APP.route('/<repo>/issue/<issueid>/add',
           methods=('GET','POST'))
@APP.route('/fork/<username>/<repo>/issue/<issueid>/add',
           methods=('GET', 'POST'))
def add_comment_issue(repo, issueid, username=None):
    ''' Add a comment to an issue. '''
    repo = progit.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        flask.abort(404, 'Project not found')

    if not repo.issue_tracker:
        flask.abort(404, 'No issue tracker found for this project')

    issue = progit.lib.get_issue(SESSION, issueid)

    if issue is None or issue.project != repo:
        flask.abort(404, 'Issue not found')

    form = progit.forms.AddIssueCommentForm()
    if form.validate_on_submit():
        comment = form.comment.data

        try:
            message = progit.lib.add_issue_comment(
                SESSION,
                issue=issue,
                comment=comment,
                user=flask.g.fas_user.username,
            )
            SESSION.commit()
            flask.flash(message)
        except SQLAlchemyError, err:  # pragma: no cover
            SESSION.rollback()
            flask.flash(str(err), 'error')

    return flask.redirect(flask.url_for(
        'view_issue', username=username, repo=repo.name, issueid=issue.id))


@APP.route('/<repo>/issues')
@APP.route('/fork/<username>/<repo>/issues')
def view_issues(repo, username=None):
    """ List all issues associated to a repo
    """
    status = flask.request.args.get('status', None)

    repo = progit.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        flask.abort(404, 'Project not found')

    if not repo.issue_tracker:
        flask.abort(404, 'No issue tracker found for this project')

    if status is not None:
        if status.lower() == 'closed':
            issues = progit.lib.get_issues(SESSION, repo, closed=True)
        else:
            issues = progit.lib.get_issues(SESSION, repo, status=status)
    else:
        issues = progit.lib.get_issues(SESSION, repo, status='Open')

    return flask.render_template(
        'issues.html',
        select='issues',
        repo=repo,
        username=username,
        status=status,
        issues=issues,
    )


@APP.route('/<repo>/new_issue', methods=('GET', 'POST'))
@APP.route('/fork/<username>/<repo>/new_issue', methods=('GET', 'POST'))
@cla_required
def new_issue(repo, username=None):
    """ Create a new issue
    """
    repo = progit.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        flask.abort(404, 'Project not found')

    form = progit.forms.IssueForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        try:
            message = progit.lib.new_issue(
                SESSION,
                repo=repo,
                title=title,
                content=content,
                user=flask.g.fas_user.username,
            )
            SESSION.commit()
            flask.flash(message)
            return flask.redirect(flask.url_for(
                'view_fork_issues', username=username, repo=repo.name))
        except progit.exceptions.ProgitException, err:
            flask.flash(str(err), 'error')
        except SQLAlchemyError, err:  # pragma: no cover
            SESSION.rollback()
            flask.flash(str(err), 'error')

    return flask.render_template(
        'new_issue.html',
        select='issues',
        form=form,
        repo=repo,
        username=username,
    )


@APP.route('/<repo>/issue/<issueid>', methods=('GET', 'POST'))
@APP.route('/fork/<username>/<repo>/issue/<issueid>',
           methods=('GET', 'POST'))
@cla_required
def view_issue(repo, issueid, username=None):
    """ List all issues associated to a repo
    """

    repo = progit.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        flask.abort(404, 'Project not found')

    if not repo.issue_tracker:
        flask.abort(404, 'No issue tracker found for this project')

    issue = progit.lib.get_issue(SESSION, issueid)

    if issue is None or issue.project != repo:
        flask.abort(404, 'Issue not found')

    status = progit.lib.get_issue_statuses(SESSION)
    form = progit.forms.UpdateIssueStatusForm(status=status)

    if form.validate_on_submit():
        try:
            message = progit.lib.edit_issue(
                SESSION,
                issue=issue,
                status=form.status.data,
            )
            SESSION.commit()
            flask.flash(message)
            url = flask.url_for('view_issues', repo=repo.name)
            if username:
                url = flask.url_for(
                    'view_fork_issues', username=username, repo=repo.name)
            return flask.redirect(url)
        except SQLAlchemyError, err:  # pragma: no cover
            SESSION.rollback()
            flask.flash(str(err), 'error')
    elif flask.request.method == 'GET':
        form.status.data = issue.status

    return flask.render_template(
        'issue.html',
        select='issues',
        repo=repo,
        username=username,
        issue=issue,
        form=form,
    )


@APP.route('/<repo>/issue/<issueid>/edit', methods=('GET', 'POST'))
@APP.route('/fork/<username>/<repo>/issue/<issueid>/edit',
           methods=('GET', 'POST'))
@cla_required
def edit_issue(repo, issueid, username=None):
    """ Edit the specified issue
    """
    repo = progit.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        flask.abort(404, 'Project not found')

    if not repo.issue_tracker:
        flask.abort(404, 'No issue tracker found for this project')

    issue = progit.lib.get_issue(SESSION, issueid)

    if issue is None or issue.project != repo:
        flask.abort(404, 'Issue not found')

    status = progit.lib.get_issue_statuses(SESSION)
    form = progit.forms.IssueForm(status=status)
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        status = form.status.data

        try:
            message = progit.lib.edit_issue(
                SESSION,
                issue=issue,
                title=title,
                content=content,
                status=status,
            )
            SESSION.commit()
            flask.flash(message)
            url = flask.url_for(
                'view_issue', username=username,
                repo=repo.name, issueid=issue.id)
            return flask.redirect(url)
        except progit.exceptions.ProgitException, err:
            flask.flash(str(err), 'error')
        except SQLAlchemyError, err:  # pragma: no cover
            SESSION.rollback()
            flask.flash(str(err), 'error')
    elif flask.request.method == 'GET':
        form.title.data = issue.title
        form.content.data = issue.content
        form.status.data = issue.status

    return flask.render_template(
        'new_issue.html',
        select='issues',
        type='edit',
        form=form,
        repo=repo,
        username=username,
        issue=issue,
    )