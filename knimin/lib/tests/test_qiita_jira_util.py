from unittest import TestCase, main

from knimin.lib.qiita_jira_util import create_project


class TestQiitaJiraUtil(TestCase):
    def test_create_project(self):
        pj_name = 'My New Project'

        # check success
        pj, message = create_project(pj_name)
        self.assertEqual(message, '')
        self.assertEqual(pj['projectName'], pj_name)
        self.assertEqual(pj['projectKey'], 'TM10001')

        # check failure
        pj, message = create_project(pj_name)
        self.assertIsNone(pj)
        self.assertEqual(message, 'A project with that name already exists.')


if __name__ == '__main__':
    main()
