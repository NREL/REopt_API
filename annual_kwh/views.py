from django.http import JsonResponse
from annual_kwh.models import AnnualkWhModel, default_buildings


def annual_kwh(request):

    bldg = request.GET.get('load_profile_name')
    bldg = bldg.lower()
    if bldg not in default_buildings:
            raise ValueError("Invalid load_profile_name. Select from the following:\n{}"
                                          .format(default_buildings))
    try:
        lat = float(request.GET.get('latitude'))
        lon = float(request.GET.get('longitude'))
    except ValueError:
        raise ValueError("latitude or longitude contains invalid value. Please enter numeric value.")

    akm = AnnualkWhModel(bldg=bldg, latitude=lat, longitude=lon)

    response = JsonResponse(
        {'annual_kwh': akm.annual_kwh},
    )

    return response
