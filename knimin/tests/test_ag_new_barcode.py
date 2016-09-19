from unittest import main

from tornado.escape import url_escape

from knimin.tests.tornado_test_base import TestHandlerBase
from knimin import db


class TestAGBarcodePrintoutHandler(TestHandlerBase):
    def test_get_not_authed(self):
        response = self.get('/ag_new_barcode/download/')
        self.assertEqual(response.code, 405)  # Method Not Allowed

    def test_post(self):
        self.mock_login_admin()
        response = self.post('/ag_new_barcode/download/',
                             {'barcodes': "1111,222,33,4"})
        self.assertEqual(response.code, 200)
        # is it sufficient to check that the response provides a pdf-file or
        # should I somehow check the contents of the PDF?
        self.assertEqual(response.headers['Content-Disposition'],
                         'attachment; filename=barcodes.pdf')


class TestAGBarcodeAssignedHandler(TestHandlerBase):
    def test_get_not_authed(self):
        response = self.get('/ag_new_barcode/assigned/')
        self.assertEqual(response.code, 405)  # Method Not Allowed

    def test_post(self):
        self.mock_login_admin()
        projects = ["American Gut Project", "Autism Spectrum Disorder"]
        barcodes = ["1111", "222", "33", "4"]
        response = self.post('/ag_new_barcode/assigned/',
                             {'barcodes': ",".join(barcodes),
                              'projects': ",".join(projects)})
        self.assertEqual(response.code, 200)
        text = "".join(["%s\t%s\n" % (b, ",".join(projects))
                        for b in barcodes])
        self.assertEqual(response.body, text)


class TestAGNewBarcodeHandler(TestHandlerBase):
    def test_get_not_authed(self):
        response = self.get('/ag_new_barcode/')
        self.assertEqual(response.code, 200)
        port = self.get_http_port()
        self.assertEqual(response.effective_url,
                         'http://localhost:%d/login/?next=%s' %
                         (port, url_escape('/ag_new_barcode/')))

    def test_get(self):
        self.mock_login_admin()
        response = self.get('/ag_new_barcode/')
        self.assertEqual(response.code, 200)

        for project in db.getProjectNames():
            self.assertIn("<option value='%s'>%s</option>" %
                          (project, project), response.body)
        self.assertIn("Number of barcodes (%i unassigned)" %
                      len(db.get_unassigned_barcodes()), response.body)

    def test_post(self):
        self.mock_login_admin()
        # check that unkown action results in a response code 400
        response = self.post('/ag_new_barcode/', {'action': 'unkown'})
        self.assertEqual(response.code, 400)

        # TODO: test if exception for 0 barcodes to create is raised issue #105

        num_barcodes = 4
        projects = ["American Gut Project", "Autism Spectrum Disorder"]

        # check creation of new barcodes
        response = self.post('/ag_new_barcode/', {'action': 'create',
                                                  'numbarcodes': num_barcodes})
        self.assertIn("%i Barcodes created! Please wait for barcode download" %
                      num_barcodes, response.body)

        response = self.post('/ag_new_barcode/',
                             {'action': 'assign',
                              'numbarcodes': num_barcodes,
                              'projects': ",".join(projects)})

        # print()

if __name__ == "__main__":
    main()
