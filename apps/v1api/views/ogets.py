# -*- coding: utf-8 -*-
"""
bbofuser: apps.v1api.views
FILE: ogets
Created: 9/27/15 7:04 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import requests

from xml.dom import minidom

from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AbstractApplication, AccessToken
from oauth2_provider.views.generic import ProtectedResourceView, View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.v1api.views.patient import get_patient
from apps.v1api.views.crosswalk import lookup_xwalk
from apps.v1api.utils import (build_params)

class Hello(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')


class Patients(ListView):
    if settings.DEBUG:
        print("in apps.v1api.ogets.Patients")

    def get(self, request, patient_id, *args, **kwargs):
        # This is a patient profile GET
        #
        # use request.user to lookup a crosswalk
        # get the FHIR Patient ID
        # Call the FHIR Patient Profile
        # Return the result
        if settings.DEBUG:
            print("in Patients.get with", patient_id)

        xwalk_id = lookup_xwalk(request, )
        if settings.DEBUG:
            print("crosswalk:", xwalk_id)

        if xwalk_id == None:
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        if settings.DEBUG:
            print("now we need to evaluate the parameters and arguments"
                  " to work with ", xwalk_id, "and ", request.user)
            print("GET Parameters:", request.GET, ":")

        if patient_id == xwalk_id:
            key = patient_id
        else:
            key = xwalk_id.strip()

        in_fmt = "json"
        Txn = {'name': "Patient",
           'display': 'Patient',
           'mask': True,
           'server': settings.FHIR_SERVER,
           'locn': "/baseDstu2/Patient/",
           'template': 'v1api/patient.html',
           'in_fmt': in_fmt,
           }

        skip_parm = ['_id']
        pass_params = build_params(request.GET, skip_parm)

        pass_to = Txn['server'] + Txn['locn'] + key + "/"

        print("Here is the URL to send, %s now get parameters" % pass_to)

        if pass_params != "":
            pass_to = pass_to + pass_params

        try:
            r = requests.get(pass_to)

        except requests.ConnectionError:
            if settings.DEBUG:
                print("Problem connecting to FHIR Server")
            messages.error(request, "FHIR Server is unreachable." )
            return HttpResponseRedirect(reverse_lazy('api:v1:home'))

        text_out = ""
        if '_format=xml' in pass_to:
            text_out= minidom.parseString(r.text).toprettyxml()
        else:
            text_out = r.json()

        return HttpResponse('This is the Patient Pass Thru %s using %s '
                            'and with response of %s' % (xwalk_id,
                                                         pass_to,
                                                         text_out))

    # """
    # Class-based view for Patient Resource
    #
    # GET needs to mask patient elements.
    # GET must use the user info to lookup in a CrossWalk
    #
    # """

    # @cache_page(60 * 15)
    # @csrf_protect
    # def post(self, request,patient_id, *args, **kwargs):
    #
    #     messages.info(request, "POST not implemented")
    #     if settings.DEBUG:
    #         print("We are in the apps.v1api.views.oget.Patients.post")
    #     return HttpResponseRedirect(reverse_lazy('ap:v1:home'))


@protected_resource()
def patient(request, *args, **kwargs):
    # TODO: get this working

    if settings.DEBUG:
        print("in apps.v1api.views.ogets.Patient")
        print("request:", request)

    result = get_patient(request, *args, **kwargs)
    if settings.DEBUG:
        print("Results:", result)

    return result
