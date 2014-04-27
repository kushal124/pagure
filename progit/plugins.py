#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import flask
import os
import sys
from math import ceil

import pygit2
from sqlalchemy.exc import SQLAlchemyError
from straight.plugin import load
from hooks import BaseHook

import progit.exceptions
import progit.lib
import progit.forms
from progit import (APP, SESSION, LOG, __get_file_in_tree, cla_required,
                    is_repo_admin)


def get_plugin_names():
    ''' Return the list of plugins names. '''
    plugins = load('progit.hooks', subclasses=BaseHook)
    output = [plugin.name for plugin in plugins]
    return output


def get_plugin(plugin_name):
    ''' Return the list of plugins names. '''
    plugins = load('progit.hooks', subclasses=BaseHook)
    for plugin in plugins:
        if plugin.name == plugin_name:
            return plugin


@APP.route('/<repo>/settings/<plugin>', methods=('GET', 'POST'))
@APP.route('/fork/<username>/<repo>/settings/<plugin>', methods=('GET', 'POST'))
@cla_required
def view_plugin(repo, plugin, username=None):
    """ Presents the settings of the project.
    """
    return view_plugin_page(repo, plugin, username=username, full=True)


@APP.route(
    '/<repo>/settings/<plugin>/<int:full>', methods=('GET', 'POST'))
@APP.route(
    '/fork/<username>/<repo>/settings/<plugin>/<int:full>',
    methods=('GET', 'POST'))
@cla_required
def view_plugin_page(repo, plugin, full, username=None):
    """ Presents the settings of the project.
    """
    repo = progit.lib.get_project(SESSION, repo, user=username)

    if not repo:
        flask.abort(404, 'Project not found')

    if not is_repo_admin(repo):
        flask.abort(
            403,
            'You are not allowed to change the settings for this project')

    plugin = get_plugin(plugin)
    fields = []
    for field in plugin.form_fields:
        fields.append(getattr(plugin.form, field))

    return flask.render_template(
        'plugin.html',
        select='settings',
        full=full,
        repo=repo,
        username=username,
        plugin=plugin,
        form=plugin.form,
        fields=fields,
    )


