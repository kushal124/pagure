import json
import pygit2
    def test_view_file(self):
        """ Test the view_file endpoint. """
        output = self.app.get('/foo/blob/foo/sources')
        # No project registered in the DB
        self.assertEqual(output.status_code, 404)

        tests.create_projects(self.session)

        output = self.app.get('/test/blob/foo/sources')
        # No git repo associated
        self.assertEqual(output.status_code, 404)

        tests.create_projects_git(tests.HERE)

        output = self.app.get('/test/blob/foo/sources')
        self.assertEqual(output.status_code, 404)

        # Add some content to the git repo
        tests.add_content_git_repo(os.path.join(tests.HERE, 'test.git'))
        tests.add_readme_git_repo(os.path.join(tests.HERE, 'test.git'))
        tests.add_binary_git_repo(
            os.path.join(tests.HERE, 'test.git'), 'test.jpg')
        tests.add_binary_git_repo(
            os.path.join(tests.HERE, 'test.git'), 'test_binary')

        output = self.app.get('/test/blob/master/foofile')
        self.assertEqual(output.status_code, 404)

        # View in a branch
        output = self.app.get('/test/blob/master/sources')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            '<tr><td class="cell1"><a id="_1" href="#_1">1</a></td>'
            in output.data)
        self.assertTrue(
            '<td class="cell2"><pre> bar</pre></td>' in output.data)

        # View what's supposed to be an image
        output = self.app.get('/test/blob/master/test.jpg')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            'Binary files cannot be rendered.<br/>' in output.data)

        # View by commit id
        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        output = self.app.get('/test/blob/%s/test.jpg' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            'Binary files cannot be rendered.<br/>' in output.data)

        # View by image name -- somehow we support this
        output = self.app.get('/test/blob/sources/test.jpg')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            'Binary files cannot be rendered.<br/>'
            in output.data)

        # View binary file
        output = self.app.get('/test/blob/sources/test_binary')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            'Binary files cannot be rendered.<br/>'
            in output.data)

        # View folder
        output = self.app.get('/test/blob/master/folder1')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="tree_list">' in output.data)
        self.assertTrue('<h3>Tree</h3>' in output.data)
        self.assertTrue(
            '<a href="/test/blob/master/folder1/folder2">' in output.data)

        # View by image name -- with a non-existant file
        output = self.app.get('/test/blob/sources/testfoo.jpg')
        self.assertEqual(output.status_code, 404)
        output = self.app.get('/test/blob/master/folder1/testfoo.jpg')
        self.assertEqual(output.status_code, 404)

        # Add a fork of a fork
        item = progit.lib.model.Project(
            user_id=1,  # pingou
            name='test3',
            description='test project #3',
            parent_id=1,
        )
        self.session.add(item)
        self.session.commit()

        tests.add_content_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'))
        tests.add_readme_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'))
        tests.add_commit_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'),
            ncommits=10)

        output = self.app.get('/fork/pingou/test3/blob/master/sources')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="file_content">' in output.data)
        self.assertTrue(
            '<tr><td class="cell1"><a id="_1" href="#_1">1</a></td>'
            in output.data)
        self.assertTrue(
            '<td class="cell2"><pre> barRow 0</pre></td>' in output.data)

    def test_view_raw_file(self):
        """ Test the view_raw_file endpoint. """
        output = self.app.get('/foo/raw/foo/sources')
        # No project registered in the DB
        self.assertEqual(output.status_code, 404)

        tests.create_projects(self.session)

        output = self.app.get('/test/raw/foo/sources')
        # No git repo associated
        self.assertEqual(output.status_code, 404)

        tests.create_projects_git(tests.HERE)

        output = self.app.get('/test/raw/foo/sources')
        self.assertEqual(output.status_code, 404)

        # Add some content to the git repo
        tests.add_content_git_repo(os.path.join(tests.HERE, 'test.git'))
        tests.add_readme_git_repo(os.path.join(tests.HERE, 'test.git'))
        tests.add_binary_git_repo(
            os.path.join(tests.HERE, 'test.git'), 'test.jpg')
        tests.add_binary_git_repo(
            os.path.join(tests.HERE, 'test.git'), 'test_binary')

        output = self.app.get('/test/raw/master/foofile')
        self.assertEqual(output.status_code, 404)

        # View in a branch
        output = self.app.get('/test/raw/master/sources')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('foo\n bar' in output.data)

        # View what's supposed to be an image
        output = self.app.get('/test/raw/master/test.jpg')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(output.data.startswith('<89>PNG^M'))

        # View by commit id
        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        output = self.app.get('/test/raw/%s/test.jpg' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(output.data.startswith('<89>PNG^M'))

        # View by image name -- somehow we support this
        output = self.app.get('/test/raw/sources/test.jpg')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(output.data.startswith('<89>PNG^M'))

        # View binary file
        output = self.app.get('/test/raw/sources/test_binary')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(output.data.startswith('<89>PNG^M'))

        # View folder
        output = self.app.get('/test/raw/master/folder1')
        self.assertEqual(output.status_code, 404)

        # View by image name -- with a non-existant file
        output = self.app.get('/test/raw/sources/testfoo.jpg')
        self.assertEqual(output.status_code, 404)
        output = self.app.get('/test/raw/master/folder1/testfoo.jpg')
        self.assertEqual(output.status_code, 404)

        output = self.app.get('/test/raw/master/')
        self.assertEqual(output.status_code, 404)

        output = self.app.get('/test/raw/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(output.data.startswith(
            'diff --git a/test_binary b/test_binary\n'))

        # Add a fork of a fork
        item = progit.lib.model.Project(
            user_id=1,  # pingou
            name='test3',
            description='test project #3',
            parent_id=1,
        )
        self.session.add(item)
        self.session.commit()

        tests.add_content_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'))
        tests.add_readme_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'))
        tests.add_commit_git_repo(
            os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'),
            ncommits=10)

        output = self.app.get('/fork/pingou/test3/raw/master/sources')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('foo\n bar' in output.data)

    def test_view_commit(self):
        """ Test the view_commit endpoint. """
        output = self.app.get('/foo/bar')
        # No project registered in the DB
        self.assertEqual(output.status_code, 404)

        tests.create_projects(self.session)

        output = self.app.get('/test/bar')
        # No git repo associated
        self.assertEqual(output.status_code, 404)

        tests.create_projects_git(tests.HERE)

        output = self.app.get('/test/bar')
        self.assertEqual(output.status_code, 404)

        # Add a README to the git repo - First commit
        tests.add_readme_git_repo(os.path.join(tests.HERE, 'test.git'))
        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        # View first commit
        output = self.app.get('/test/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="commit_diff">' in output.data)
        self.assertTrue('<th>Author</th>' in output.data)
        self.assertTrue('<th>Committer</th>' in output.data)
        self.assertTrue(
            '<span style="color: #00A000">+ ProGit</span>' in output.data)
        self.assertTrue(
            '<span style="color: #00A000">+ ======</span>' in output.data)

        # Add some content to the git repo
        tests.add_content_git_repo(os.path.join(tests.HERE, 'test.git'))

        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        # View another commit
        output = self.app.get('/test/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="commit_diff">' in output.data)
        self.assertTrue('<th>Author</th>' in output.data)
        self.assertTrue('<th>Committer</th>' in output.data)
        self.assertTrue(
            '<div class="highlight" style="background: #f8f8f8">'
            '<pre style="line-height: 125%">'
            '<span style="color: #800080; font-weight: bold">'
            '@@ -0,0 +1,3 @@</span>' in output.data)

        # Add a fork of a fork
        item = progit.lib.model.Project(
            user_id=1,  # pingou
            name='test3',
            description='test project #3',
            parent_id=1,
        )
        self.session.add(item)
        self.session.commit()
        forkedgit = os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git')

        tests.add_content_git_repo(forkedgit)
        tests.add_readme_git_repo(forkedgit)

        repo = pygit2.init_repository(forkedgit)
        commit = repo.revparse_single('HEAD')

        # Commit does not exist in anothe repo :)
        output = self.app.get('/test/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 404)

        # View commit of fork
        output = self.app.get('/fork/pingou/test3/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<section class="commit_diff">' in output.data)
        self.assertTrue('<th>Author</th>' in output.data)
        self.assertTrue('<th>Committer</th>' in output.data)
        self.assertTrue(
            '<span style="color: #00A000">+ ProGit</span>' in output.data)
        self.assertTrue(
            '<span style="color: #00A000">+ ======</span>' in output.data)

    def test_view_commit_patch(self):
        """ Test the view_commit_patch endpoint. """
        output = self.app.get('/foo/bar.patch')
        # No project registered in the DB
        self.assertEqual(output.status_code, 404)

        tests.create_projects(self.session)

        output = self.app.get('/test/bar.patch')
        # No git repo associated
        self.assertEqual(output.status_code, 404)

        tests.create_projects_git(tests.HERE)

        output = self.app.get('/test/bar.patch')
        self.assertEqual(output.status_code, 404)

        # Add a README to the git repo - First commit
        tests.add_readme_git_repo(os.path.join(tests.HERE, 'test.git'))
        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        # View first commit
        output = self.app.get('/test/%s.patch' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('''diff --git a/README.rst b/README.rst
new file mode 100644
index 0000000..10d2e1c
--- /dev/null
+++ b/README.rst
@@ -0,0 +1,17 @@
+ProGit
+======
+
+:Author: Pierre-Yves Chibon <pingou@pingoured.fr>
+
+
+ProGit is a light-weight git-centered forge based on pygit2.
+
+Currently, ProGit offers a decent web-interface for git repositories, a
+simplistic ticket system (that needs improvements) and possibilities to create
+new projects, fork existing ones and create/merge pull-requests across or
+within projects.
+
+
+Homepage: https://github.com/pypingou/ProGit
+
+Dev instance: http://209.132.184.222/ (/!\ May change unexpectedly, it's a dev instance ;-))
''' in output.data)
        self.assertTrue('Subject: Add a README file' in output.data)

        # Add some content to the git repo
        tests.add_content_git_repo(os.path.join(tests.HERE, 'test.git'))

        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        # View another commit
        output = self.app.get('/test/%s.patch' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            'Subject: Add some directory and a file for more testing'
            in output.data)
        self.assertTrue('''diff --git a/folder1/folder2/file b/folder1/folder2/file
new file mode 100644
index 0000000..11980b1
--- /dev/null
+++ b/folder1/folder2/file
@@ -0,0 +1,3 @@
+foo
+ bar
+baz
\ No newline at end of file
''' in output.data)

        # Add a fork of a fork
        item = progit.lib.model.Project(
            user_id=1,  # pingou
            name='test3',
            description='test project #3',
            parent_id=1,
        )
        self.session.add(item)
        self.session.commit()
        forkedgit = os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git')

        tests.add_content_git_repo(forkedgit)
        tests.add_readme_git_repo(forkedgit)

        repo = pygit2.init_repository(forkedgit)
        commit = repo.revparse_single('HEAD')

        # Commit does not exist in anothe repo :)
        output = self.app.get('/test/%s.patch' % commit.oid.hex)
        self.assertEqual(output.status_code, 404)

        # View commit of fork
        output = self.app.get('/fork/pingou/test3/%s.patch' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('''diff --git a/README.rst b/README.rst
new file mode 100644
index 0000000..10d2e1c
--- /dev/null
+++ b/README.rst
@@ -0,0 +1,17 @@
+ProGit
+======
+
+:Author: Pierre-Yves Chibon <pingou@pingoured.fr>
+
+
+ProGit is a light-weight git-centered forge based on pygit2.
+
+Currently, ProGit offers a decent web-interface for git repositories, a
+simplistic ticket system (that needs improvements) and possibilities to create
+new projects, fork existing ones and create/merge pull-requests across or
+within projects.
+
+
+Homepage: https://github.com/pypingou/ProGit
+
+Dev instance: http://209.132.184.222/ (/!\ May change unexpectedly, it's a dev instance ;-))
''' in output.data)

    def test_view_tree(self):
        """ Test the view_tree endpoint. """
        output = self.app.get('/foo/tree/')
        # No project registered in the DB
        self.assertEqual(output.status_code, 404)

        tests.create_projects(self.session)

        output = self.app.get('/test/tree/')
        # No git repo associated
        self.assertEqual(output.status_code, 404)

        tests.create_projects_git(tests.HERE)

        output = self.app.get('/test/tree/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<h2>\n    <a href="/test/tree/">None</a>/</h2>' in output.data)
        self.assertTrue(
            'No content found in this repository' in output.data)

        # Add a README to the git repo - First commit
        tests.add_readme_git_repo(os.path.join(tests.HERE, 'test.git'))
        repo = pygit2.init_repository(os.path.join(tests.HERE, 'test.git'))
        commit = repo.revparse_single('HEAD')

        # View first commit
        output = self.app.get('/test/tree/%s' % commit.oid.hex)
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<p>test project #1</p>' in output.data)
        self.assertTrue('<h3>Tree</h3>' in output.data)
        self.assertTrue('README.rst' in output.data)
        self.assertFalse(
            'No content found in this repository' in output.data)

        # View tree by branch
        output = self.app.get('/test/tree/master')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<p>test project #1</p>' in output.data)
        self.assertTrue('<h3>Tree</h3>' in output.data)
        self.assertTrue('README.rst' in output.data)
        self.assertFalse(
            'No content found in this repository' in output.data)

        # Add a fork of a fork
        item = progit.lib.model.Project(
            user_id=1,  # pingou
            name='test3',
            description='test project #3',
            parent_id=1,
        )
        self.session.add(item)
        self.session.commit()
        forkedgit = os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git')

        tests.add_content_git_repo(forkedgit)

        output = self.app.get('/fork/pingou/test3/tree/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<p>test project #3</p>' in output.data)
        self.assertTrue('<h3>Tree</h3>' in output.data)
        self.assertTrue(
            '<a href="/fork/pingou/test3/blob/master/folder1">'
            in output.data)
        self.assertTrue(
            '<a href="/fork/pingou/test3/blob/master/sources">'
            in output.data)
        self.assertFalse(
            'No content found in this repository' in output.data)

    def test_delete_repo(self):
        """ Test the delete_repo endpoint. """
        output = self.app.post('/foo/delete')
        # User not logged in
        self.assertEqual(output.status_code, 302)

        user = tests.FakeUser()
        with tests.user_set(progit.APP, user):
            output = self.app.post('/foo/delete')
            # No project registered in the DB
            self.assertEqual(output.status_code, 404)

            tests.create_projects(self.session)

            output = self.app.post('/test/delete')
            # No git repo associated
            self.assertEqual(output.status_code, 403)

        user = tests.FakeUser(username='pingou')
        with tests.user_set(progit.APP, user):
            output = self.app.post('/test/delete', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="error">Could not delete all the repos from the '
                'system</li>' in output.data)
            self.assertTrue('<h2>Projects (1)</h2>' in output.data)
            self.assertTrue('<h2>Forks (0)</h2>' in output.data)

            # Only git repo
            item = progit.lib.model.Project(
                user_id=1,  # pingou
                name='test',
                description='test project #1',
            )
            self.session.add(item)
            self.session.commit()
            tests.create_projects_git(tests.HERE)
            output = self.app.post('/test/delete', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="error">Could not delete all the repos from the '
                'system</li>' in output.data)
            self.assertTrue('<h2>Projects (1)</h2>' in output.data)
            self.assertTrue('<h2>Forks (0)</h2>' in output.data)

            # Only git and doc repo
            item = progit.lib.model.Project(
                user_id=1,  # pingou
                name='test',
                description='test project #1',
            )
            self.session.add(item)
            self.session.commit()
            tests.create_projects_git(tests.HERE)
            tests.create_projects_git(os.path.join(tests.HERE, 'docs'))
            output = self.app.post('/test/delete', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="error">Could not delete all the repos from the '
                'system</li>' in output.data)

            # All repo there
            item = progit.lib.model.Project(
                user_id=1,  # pingou
                name='test',
                description='test project #1',
            )
            self.session.add(item)
            self.session.commit()
            tests.create_projects_git(tests.HERE)
            tests.create_projects_git(os.path.join(tests.HERE, 'docs'))
            tests.create_projects_git(os.path.join(tests.HERE, 'tickets'))
            output = self.app.post('/test/delete', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<h2>Projects (1)</h2>' in output.data)
            self.assertTrue('<h2>Forks (0)</h2>' in output.data)

            # Add a fork of a fork
            item = progit.lib.model.Project(
                user_id=1,  # pingou
                name='test3',
                description='test project #3',
                parent_id=1,
            )
            self.session.add(item)
            self.session.commit()
            tests.add_content_git_repo(
                os.path.join(tests.HERE, 'forks', 'pingou', 'test3.git'))
            tests.add_content_git_repo(
                os.path.join(tests.HERE, 'docs', 'pingou', 'test3.git'))
            tests.add_content_git_repo(
                os.path.join(tests.HERE, 'tickets', 'pingou', 'test3.git'))

            output = self.app.post(
                '/fork/pingou/test3/delete', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<h2>Projects (1)</h2>' in output.data)
            self.assertTrue('<h2>Forks (0)</h2>' in output.data)
