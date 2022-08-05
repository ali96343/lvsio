from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS


import os, sys
from math import sqrt
from random import randint
from time import sleep, time
from datetime import datetime
import json



@action("ex1/ctrl1", )
def ctrl1():
     return "ex1_ctrl1"

