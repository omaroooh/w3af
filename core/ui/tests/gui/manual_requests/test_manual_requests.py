'''
test_manual_requests.py

Copyright 2013 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
import os

from core.ui.tests.wrappers.xpresser_unittest import XpresserUnittest

from core.data.url.tests.helpers.http_daemon import HTTPDaemon
from core.data.parsers.HTTPRequestParser import HTTPRequestParser

# TODO: Code duplication
#
# Tried to do this the right way, by adding the import at the beginning
# of the file:
#
#from core.ui.gui.tools.manual_requests import MANUAL_REQUEST_EXAMPLE
#
# But it fails because of the pygtk vs. gi stuff... 
MANUAL_REQUEST_EXAMPLE = """\
GET http://localhost/script.php HTTP/1.0
Host: www.some_host.com
User-Agent: w3af.org
Pragma: no-cache
Content-Type: application/x-www-form-urlencoded
"""


class TestManualRequests(XpresserUnittest):
    
    IMAGES = os.path.join('core', 'ui', 'tests', 'gui', 'manual_requests', 'images')
    EXTRA_IMAGES = os.path.join('core', 'ui', 'tests', 'gui', 'tools_menu', 'images')
    
    def setUp(self):
        XpresserUnittest.setUp(self)
        self.click('manual-request')

    def tearDown(self):
        self.click('close-with-cross')
        XpresserUnittest.tearDown(self)
    
    def test_offline_url(self):
        self.double_click('localhost')
        self.type('moth:8081', False)
        
        self.click('send')
        self.find('stopped_sending_requests')
        
        # Close the error dialog
        self.type(['<Enter>',], False)

    def test_GET_request(self):
        self.http_daemon = HTTPDaemon()
        self.http_daemon.start()
        self.http_daemon.wait_for_start()
        
        #
        #    Send the request to our server using the GUI
        #
        self.double_click('localhost')
        self.type('127.0.0.1:%s' % self.http_daemon.get_port(), False)
        
        self.click('send')
        
        # Wait until we actually get the response, and verify we got the
        # response body we expected:
        self.find('abcdef')
        self.find('200_OK')
        
        #
        #    Assert that it's what we really expected
        #
        requests = self.http_daemon.requests
        self.assertEqual(len(requests), 1)
        
        request = requests[0]

        head, postdata = MANUAL_REQUEST_EXAMPLE, ''
        http_request = HTTPRequestParser(head, postdata)
        
        self.assertEqual(http_request.get_url().get_path(), request.path)
        self.assertEqual(http_request.get_method(), request.command)
        
        for header_name, header_value in http_request.get_headers().iteritems():
            self.assertIn(header_name.lower(), request.headers)
            self.assertEqual(header_value, request.headers[header_name.lower()])
            
        self.http_daemon.server.shutdown()