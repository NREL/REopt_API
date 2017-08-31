from django.http import JsonResponse, HttpResponseBadRequest
from reo.models import RunOutput
from models import ResilienceModel
from reo.utilities import API_Error

def resilience_stats(request):
    uuid = request.GET.get('run_uuid')

    try:
        run_output = RunOutput.objects.get(uuid=uuid)
    except Exception as e:
        return API_Error(e).response

    rm = ResilienceModel.create(run_output=run_output)

    response = JsonResponse(
        {'resilience_by_timestep': rm.resilience_by_timestep,
         'resilience_hours_min': rm.resilience_hours_min,
         'resilience_hours_max': rm.resilience_hours_max,
         'resilience_hours_avg': rm.resilience_hours_avg,
         'outage_durations': rm.outage_durations,
         'probs_of_surviving': rm.probs_of_surviving,
        }
    )
    return response
