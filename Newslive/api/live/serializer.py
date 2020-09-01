import json

from rest_framework import serializers
from . import models


def ser_data(data):
    data = json.dumps(data)
    return data