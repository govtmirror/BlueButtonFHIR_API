from django.shortcuts import render

from fhir.settings import DF_EXTRA_INFO
from fhir.utils import kickout_404, kickout_400, kickout_500
from fhir.views.update import update
from fhir.views.delete import delete
from fhir.views.read import read

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def read_or_update_or_delete(request, resource_type, id):
    """Route to read, update, or delete based on HTTP method FHIR Interaction"""

    if request.method == 'GET':
        # Read
        return read(request, resource_type, id)
    elif request.method == 'PUT':
        # update
        return update(request, resource_type, id)
    elif request.method == 'DELETE':
        # delete
        return delete(request, resource_type, id)
    #else:
    # Not supported.
    msg = "HTTP method %s not supported at this URL." % (request.method)
    return kickout_400(msg)
    
    
