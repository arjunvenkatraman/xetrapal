#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module initializes a Thespian actor system.

It sets up a global ActorSystem, likely intended for use by other
parts of the Xetrapal application that leverage the Thespian actor model
for concurrent or distributed processing. The system is configured
to use 'multiprocTCPBase'.
"""
"""
Created on Fri Mar 16 12:21:26 2018

@author: anandabhairav
"""

from thespian.actors import *
ActorSystem("multiprocTCPBase")
vidhata=ActorSystem()
