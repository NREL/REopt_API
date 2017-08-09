

class Site(object):

    def __init__(self, land_area=None, roof_area=None, **kwargs):

        self.land_acres = land_area
        self.roof_squarefeet = roof_area
