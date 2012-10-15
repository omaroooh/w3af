'''
utils.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.
    
w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
'''
from core.data.request.fuzzable_request import fuzzable_request
from core.data.dc.header import Header

#Keys representing CORS headers for manipulations.
ACCESS_CONTROL_ALLOW_ORIGIN = "ACCESS-CONTROL-ALLOW-ORIGIN"
ACCESS_CONTROL_ALLOW_METHODS = "ACCESS-CONTROL-ALLOW-METHODS"
ACCESS_CONTROL_ALLOW_HEADERS = "ACCESS-CONTROL-ALLOW-HEADERS"
ACCESS_CONTROL_ALLOW_MAX_AGE = "ACCESS-CONTROL-ALLOW-MAX-AGE"
ACCESS_CONTROL_ALLOW_CREDENTIALS = "ACCESS-CONTROL-ALLOW-MAX-CREDENTIALS"        


def provides_cors_features(freq, url_opener):
    '''
    Method to detect if url provides CORS features.
    
    @param freq: A fuzzableRequest object.
    @param url_opener: "core.data.url.xUrllib" class instance to use for 
                       HTTP request/response processing.
    @return: True if the URL provides CORS features, False otherwise. 
    '''        
    response = url_opener.GET(freq.getURL())
    
    ac_value = retrieve_cors_header(response, ACCESS_CONTROL_ALLOW_ORIGIN)
    if ac_value is not None:
        return True
    
    headers = Header({'Origin': 'www.w3af.org'})
    response = url_opener.GET(freq.getURL(), headers=headers)
    ac_value = retrieve_cors_header(response, ACCESS_CONTROL_ALLOW_ORIGIN)
    if ac_value is not None:
        return True
    
    return False             
   
   
def retrieve_cors_header(response, key):   
    '''
    Method to retrieve a CORS header value from a HTTP response.
    
    @param response: A httpResponse object.
    @param key: A key representing the desired header value to retrieve.
    @return: The header value or None if the header do not exists. 
    '''
    headers = response.getHeaders()
    
    for header_name in headers:
        if header_name.upper().strip() == key.upper():                
            return headers[header_name]
    
    return None


def build_cors_request(url, origin_header_value):
    '''
    Method to generate a "GET" CORS HTTP request based on input context. 

    @param url: A url_object object.
    @param origin_header_value: Value of the "ORIGIN" HTTP request header
                                  (if value is set to None then the "ORIGIN"
                                  header is skipped).
    @return: A fuzzable request that will be sent to @url and has
             @origin_header_value in the Origin header.
    '''
    headers = Header()
    if origin_header_value != None:
        headers["Origin"] = origin_header_value.strip()           
    
    forged_req = fuzzable_request(url, 'GET', headers=headers)
    return forged_req