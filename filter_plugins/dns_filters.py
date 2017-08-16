from jinja2.exceptions import FilterArgumentError


class InvalidRdata(FilterArgumentError):

    def __init__(self, message):
        super().__init__(u'InvalidRdata: {}'.format(message))

def rdata_constructor(constructor):
    def wrapper(resource):
        try:
            return ' '.join([str(field) for field in [resource['name'],
                                                      resource['ttl'],
                                                      resource['class'],
                                                      resource['type'],
                                                      constructor(resource)]])
        except KeyError as error:
            raise InvalidRdata('Missing required field {error}\n{resource}'.format(error=error, resource=resource))
    return wrapper

def simple_rdata_constructor_constructor(field):
    @rdata_constructor
    def simple_rdata_constructor(resource):
        rdata = resource.get('value') or resource.get(field)
        if not rdata:
            raise KeyError(field)
        return rdata
    return simple_rdata_constructor

@rdata_constructor
def construct_NS_rdata(resource):
    return resource.get('nsdname',
                        '{nshost}.ns.{name}'.format( nshost=resource['nshost'],
                                                         name=resource['name'] ))

@rdata_constructor
def construct_SOA_rdata(resource):
    return '{mname} {rname} {serial} {refresh} {retry} {expire} {minimum}'.format(
         mname=resource.get('mname',
                            '{nshost}.ns.{name}'.format( nshost=resource['nshost'],
                                                         name=resource['name'] )),
         rname=resource.get('rname',
                            'hostmaster.{name}'.format( nshost=resource['nshost'],
                                                         name=resource['name'] )),
         serial=resource['serial'],
         refresh=resource['refresh'],
         retry=resource['retry'],
         expire=resource['expire'],
         minimum=resource['minimum']
    )



resource_record_constructors = dict( A=simple_rdata_constructor_constructor('address'),
                                     CNAME=simple_rdata_constructor_constructor('cname'),
                                     TXT=simple_rdata_constructor_constructor('txt-data'),
                                     PTR=simple_rdata_constructor_constructor('ptrdname'),
                                     SOA=construct_SOA_rdata,
                                     NS=construct_NS_rdata )

def dns_resource_record(resource):
     constructor = resource_record_constructors[resource['type']]
     return constructor(resource)

class FilterModule(object):
    """Convert a dictionary describing a DNS record to its string representation"""
    def filters(self):
        return dict(dns_resource_record=dns_resource_record)
