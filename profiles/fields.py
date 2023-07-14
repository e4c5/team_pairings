"""
https://gist.github.com/thomasyip/3158388
https://gist.github.com/gerhc/3349202
"""
import os
import time
import json
import random

from django.db import models


START_TIME = 1375525142176

def make_id():
    '''
    inspired by http://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram
    
    If two people upload an image at the same millisecond, there is a chance of about 1 in four 
    million of a collision happening.
    '''
    
    t = int(time.time()*1000) - START_TIME
    u = random.SystemRandom().getrandbits(23)
    id = (t << 23 ) | u
    
    return id


def reverse_id(id):
    t  = id >> 23
    return t + START_TIME 

