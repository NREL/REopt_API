import numpy as np

hard_problem_labels = [
    "55fc8071682bea28da63d770",
    "55fc8076682bea28da63db4c",
    "55fc807b682bea28da63de8c",
    "55fc8086682bea28da63e824",
    "55fc8095682bea28da63f508",
    "55fc8098682bea28da63f720",
    "55fc809a682bea28da63f91e",
    "55fc80bb682bea28da641468",
    "55fc80c2682bea28da641adc",
    "55fc80db682bea28da643088",
    "55fc80df682bea28da6432e2",
    "55fc80e2682bea28da643658",
    "55fc80e8682bea28da643bf0",
    "55fc80ec682bea28da643d96",
    "55fc80f0682bea28da644102",
    "55fc80fa682bea28da644ab4",
    "55fc80fe682bea28da644cd8",
    "55fc810a682bea28da64570c",
    "55fc8115682bea28da645f70",
    "55fc8116682bea28da6460fc",
    "55fc811c682bea28da646588",
    "55fc811d682bea28da6466a6",
    "55fc812a682bea28da64723a",
    "55fc812d682bea28da647418",
    "55fc8134682bea28da647980",
    "55fc8149682bea28da648bdc",
    "55fc814c682bea28da648de4",
    "55fc8152682bea28da649260",
    "55fc815b682bea28da649ae8",
    "55fc815d682bea28da649b8e",
    "55fc8165682bea28da64a2a8",
    "55fc816f682bea28da64aa70",
    "55fc817c682bea28da64b530",
    "55fc817c682bea28da64b572",
    "55fc8184682bea28da64bc90",
    "55fc818d682bea28da64c3d0",
    "55fc818e682bea28da64c424",
    "55fc819b682bea28da64ceb8",
    "55fc81a8682bea28da64d9b6",
    "55fc81aa682bea28da64da0c",
    "55fc81ba682bea28da64e63c",
    "55fc81ba682bea28da64e63e",
    "55fc81ba682bea28da64e640",
    "55fc81bf682bea28da64e9e4",
    "55fc81bf682bea28da64e9f2",
    "55fc81bf682bea28da64e9f4",
    "55fc81d1682bea28da64f5f4",
    "564cc3aa682bea7c6da13d7e",
    "5674380e682bea66ae6e650b",
    "56a0268a682bea04e8d61f09",
    "56d4bf62682bea39e58c68ae",
    "57851786682bea69ad518eec",
    "57b5ed16682bea674e2657ff",
    "58c2db92682bea35f59437b1",
    "58d3f103682bea0c5b66a7db",
    "58dd47a2682bea42a40b9cd3",
    "59121fc2682bea4a4e354c7e",
    "59a9c6ce682bea056dafab33",
    "59a9ca52682bea072bc228d8",
    "59a9cdd6682bea08fcb1fd35",
    "59a9cdd6682bea08fcb1fd37",
    "59a9cdd6682bea08fcb1fd39",
    "59a9d15a682bea0abb4a4684",
    "59a9d862682bea0e89e64357",
    "59a9dbe6682bea1096668fdb",
    "59a9dbe6682bea1096668fdd",
    "59a9dbe6682bea1096668fdf",
    "59a9e2ee682bea13e94b4429",
    "59a9e2ee682bea13e94b442b",
    "59a9e2ee682bea13e94b442d",
    "59a9e2ee682bea13e94b442f",
    "59a9e9f6682bea17a0112a4c",
    "59a9ed7a682bea1961931e25",
    "59af21e6682bea6eb0a1c857",
    "59af21e6682bea6eb0a1c859",
    "59b04cba682bea0d02dfce02",
    "59b04cba682bea0d02dfce04",
    "59b0752e682bea2157b91d3c",
    "59b0752e682bea2157b91d3e",
    "59b0752e682bea2157b91d56",
    "59b0752e682bea2157b91d5a",
]


class URDB_RateValidator:

    # map to tell if a field requires one or more other fields
    dependencies = {
        'demandweekdayschedule': ['demandratestructure'],
        'demandweekendschedule': ['demandratestructure'],
        'demandratestructure': ['demandweekdayschedule', 'demandweekendschedule'],
        'energyweekdayschedule': ['energyratestructure'],
        'energyweekendschedule': ['energyratestructure'],
        'energyratestructure': ['energyweekdayschedule', 'energyweekendschedule'],
        'flatdemandmonths': ['flatdemandstructure'],
        'flatdemandstructure': ['flatdemandmonths'],
    }

    def __init__(self, **kwargs):
        """
        Takes a dictionary parsed from a URDB Rate Json response
        - See http://en.openei.org/services/doc/rest/util_rates/?version=3

        Rates may or mat not have the following keys:

            label                       Type: string
            utility                     Type: string
            name                        Type: string
            uri                         Type: URI
            approved                    Type: boolean
            startdate                   Type: integer
            enddate                     Type: integer
            supercedes                  Type: string
            sector                      Type: string
            description                 Type: string
            source                      Type: string
            sourceparent                Type: URI
            basicinformationcomments    Type: string
            peakkwcapacitymin           Type: decimal
            peakkwcapacitymax           Type: decimal
            peakkwcapacityhistory       Type: decimal
            peakkwhusagemin             Type: decimal
            peakkwhusagemax             Type: decimal
            peakkwhusagehistory         Type: decimal
            voltageminimum              Type: decimal
            voltagemaximum              Type: decimal
            voltagecategory             Type: string
            phasewiring                 Type: string
            flatdemandunit              Type: string
            flatdemandstructure         Type: array
            demandrateunit              Type: string
            demandweekdayschedule       Type: array
            demandratchetpercentage     Type: array
            demandwindow                Type: decimal
            demandreactivepowercharge   Type: decimal
            coincidentrateunit          Type: string
            coincidentratestructure     Type: array
            coincidentrateschedule      Type: array
            demandattrs                 Type: array
            demandcomments              Type: string
            usenetmetering              Type: boolean
            energyratestructure         Type: array
            energyweekdayschedule       Type: array
            energyweekendschedule       Type: array
            energyattrs                 Type: array
            energycomments              Type: string
            fixedmonthlycharge          Type: decimal
            minmonthlycharge            Type: decimal
            annualmincharge             Type: decimal
        """
        self.errors = []  # Catch Errors - write to output file
        self.warnings = []  # Catch Warnings
        kwargs.setdefault("label", "custom")
        for key in kwargs:  # Load in attributes
            setattr(self, key, kwargs[key])
        self.numbers = [
            'fixedmonthlycharge',
            'fixedchargefirstmeter',
            'mincharge',
            'minmonthlycharge',
            'annualmincharge',
            'peakkwcapacitymin',
        ]
        self.validate()  # Validate attributes

        # TODO save errors in database? (v1 did but we never used them)

    def validate(self):
        # Check if in known hard problems
        if self.label in hard_problem_labels:
            self.errors.append(
                "URDB Rate (label={}) is currently restricted due to performance limitations".format(self.label))

        # Validate each attribute with custom valdidate function
        required_fields = ['energyweekdayschedule', 'energyweekendschedule', 'energyratestructure']
        for f in required_fields:
            if self.isNotNone(f):
                self.isNotEmptyList(f)

        for key in dir(self):
            if key in self.numbers:
                self.validate_number(key)
            else:
                v = 'validate_' + key
                if hasattr(self, v):
                    getattr(self, v)()

    @property
    def isValid(self):
        # True if no errors found during validation on init
        return self.errors == []

    # CUSTOM VALIDATION FUNCTIONS FOR EACH URDB ATTRIBUTE name validate_<attribute name>

    def validate_demandratestructure(self):
        name = 'demandratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_demandweekdayschedule(self):
        name = 'demandweekdayschedule'
        self.validCompleteHours(name, [12, 24])
        if self.validDependencies(name):
            self.validSchedule(name, 'demandratestructure')

    def validate_demandweekendschedule(self):
        name = 'demandweekendschedule'
        self.validCompleteHours(name, [12, 24])
        if self.validDependencies(name):
            self.validSchedule(name, 'demandratestructure')

    def validate_energyweekendschedule(self):
        name = 'energyweekendschedule'
        self.validCompleteHours(name, [12, 24])
        if self.validDependencies(name):
            self.validSchedule(name, 'energyratestructure')

    def validate_energyweekdayschedule(self):
        name = 'energyweekdayschedule'
        self.validCompleteHours(name, [12, 24])
        if self.validDependencies(name):
            self.validSchedule(name, 'energyratestructure')

    def validate_energyratestructure(self):
        name = 'energyratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_flatdemandstructure(self):
        name = 'flatdemandstructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_flatdemandmonths(self):
        name = 'flatdemandmonths'
        self.validCompleteHours(name, [12])
        if self.validDependencies(name):
            self.validSchedule(name, 'flatdemandstructure')

    def validate_coincidentratestructure(self):
        name = 'coincidentratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_coincidentrateschedule(self):
        name = 'coincidentrateschedule'
        if self.validDependencies(name):
            self.validSchedule(name, 'flatdemandstructure')

    def validate_demandratchetpercentage(self):
        if type(self.demandratchetpercentage) != list:
            self.errors.append('Expecting demandratchetpercentage to be a list of 12 values.')
        if len(self.demandratchetpercentage) != 12:
            self.errors.append('Expecting demandratchetpercentage to be a list of 12 values.')

    #### FUNCTIONS TO VALIDATE ATTRIBUTES ####

    def validDependencies(self, name):
        # check that all dependent attributes exist
        # return Boolean if any errors found

        all_dependencies = self.dependencies.get(name)
        valid = True
        if all_dependencies is not None:
            for d in all_dependencies:
                error = False
                if hasattr(self, d):
                    if getattr(self, d) is None:
                        error = True
                else:
                    error = True

                if error:
                    self.errors.append("Missing %s a dependency of %s" % (d, name))
                    valid = False

        return valid

    def validCompleteHours(self, schedule_name, expected_counts):
        # check that each array in a schedule contains the correct number of entries
        # :param schedule_name: str - name of URDB rate schedule param (i.e. demandweekdayschedule, energyweekendschedule )
        # :param expected_counts: list - list of expected list lengths at each level in a nested list of lists starting with the top level,
        #                                actual lengths of lists can be even divisible by the expected length to account for
        #                                finer rate resolutions (URDB is 1hr normally, but we accept custom 30-min, 15-min, 10min...)
        # return Boolean if any errors found

        if hasattr(self, schedule_name):
            schedule = getattr(self, schedule_name)

            def recursive_search(item, level=0, entry=0):
                if type(item) == list:
                    if len(item) % expected_counts[level] != 0:
                        msg = 'Entry {} {}{} does not contain a number of entries divisible by {}'.format(
                            entry+1, 'in sublevel ' + str(level) + ' ' if level > 0 else '', schedule_name,
                            expected_counts[level]
                        )
                        self.errors.append(msg)
                        return False
                    for ii, subitem in enumerate(item):
                        recursive_search(subitem, level=level + 1, entry=ii)
                return True
            valid = recursive_search(schedule)
        return valid

    def validate_number(self, name):
        try:
            float(getattr(self, name, 0))
        except:
            self.errors.append('Entry for {} ({}) is not a valid number.'.format(name, getattr(self, name)))

    def isNotNone(self, name):
        if getattr(self, name, None) is None:
            self.errors.append('Missing valid entry for {}.'.format(name))
            return False
        return True

    def isNotEmptyList(self, name):
        if type(getattr(self, name)) != list:
            self.errors.append('Expecting a list for {}.'.format(name))
            return False
        if len(getattr(self, name)) == 0:
            self.errors.append('List is empty for {}.'.format(name))
            return False
        if None in getattr(self, name):
            self.errors.append('List for {} contains null value(s).'.format(name))
            return False
        return True

    def validRate(self, rate):
        # check that each  tier in rate structure array has a rate attribute, and that all rates except one contain a 'max' attribute
        # return Boolean if any errors found
        if hasattr(self, rate):
            valid = True

            for i, r in enumerate(getattr(self, rate)):
                if len(r) == 0:
                    self.errors.append('Missing rate information for rate ' + str(i) + ' in ' + rate + '.')
                    valid = False
                num_max_tags = 0
                for ii, t in enumerate(r):
                    if t.get('max') is not None:
                        num_max_tags += 1
                    if t.get('rate') is None and t.get('sell') is None and t.get('adj') is None:
                        self.errors.append('Missing rate/sell/adj attributes for tier ' + str(ii) + " in rate " + str(
                            i) + ' ' + rate + '.')
                        valid = False
                if len(r) > 1:
                    num_missing_max_tags = len(r) - 1 - num_max_tags
                    if num_missing_max_tags > 0:
                        self.errors.append(
                            "Missing 'max' tag for {} tiers in rate {} for {}.".format(num_missing_max_tags, i, rate))
                        valid = False
            return valid
        return False

    def validSchedule(self, schedules, rate):
        # check that each rate an a schedule array has a valid set of tiered rates in the associated rate struture attribute
        # return Boolean if any errors found
        if hasattr(self, schedules):
            valid = True
            s = getattr(self, schedules)
            if isinstance(s[0], list):
                s = np.concatenate(s)

            periods = list(set(s))

            # Loop though all periond and catch error if if exists
            if hasattr(self, rate):
                for period in periods:
                    if period > len(getattr(self, rate)) - 1 or period < 0:
                        self.errors.append(
                            '%s contains value %s which has no associated rate in %s.' % (schedules, period, rate))
                        valid = False
                return valid
            else:
                self.warnings.append('{} does not exist to check {}.'.format(rate, schedules))
        return False
