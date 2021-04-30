# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:50:56 2021

@author: cryst
"""

import requests
from requests import HTTPError, Timeout

class postprocess:
    def __init__(self):
        pass
    
    def get_parameters(self):
        pass
    
    def upload(self, check=False):
        try:
            url = "https://www.wingspect.net/api/images/"
            result = requests.get(url, timeout=10)
            result.raise_for_status()
            if check:
                print('Result code: {0}'.format(result.status_code))
                        
        except HTTPError as err:
            print('Error: {0}'.format(err))
        except Timeout as err:
            print('Request timed out: {0}'.format(err))
            

    
    