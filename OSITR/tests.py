from django.test import TestCase
import os
import sys
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings  # ✅ 让 Django 读取 settings.py 里的 MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
import pyautogui
import pytesseract
import easyocr
from PIL import Image, ImageEnhance, ImageFilter
from pynput import mouse
import json
import time
import re

from pynput import mouse
from PIL import Image

# Create your tests here.

