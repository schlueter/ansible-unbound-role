from jinja2.exceptions import FilterArgumentError


class InvalidRdata(FilterArgumentError):

    def __init__(self, message):
        super().__init__(u'InvalidRdata: {}'.format(message))

def resource_record_constructor(rdata_constructor):
    """Returns a resource record constructor which uses the rdata_constructor
to build the rdata which is joined to the common resource record fields"""
    def join_rdata_with_common_fields(resource):
        """Join common resource record fields with return value of the provided
rdata constructor.

If a KeyError is caught during execution, an InvalidRdata exception is raised,
indictaing that the field for which the KeyError was raised is required."""
        try:
            common_fields = [str(field) for field in [
                resource['name'],
                resource['ttl'],
                resource['class'],
                resource['type']
            ]]
            return ' '.join( common_fields + [rdata_constructor(resource)])
        except KeyError as error:
            raise InvalidRdata('Missing required field {error}\n{resource}'.format(
                error=error,
                resource=resource
            ))
    return join_rdata_with_common_fields

def simple_resource_record_constructor_constructor(field):
    """Returns a simple rdata constructor which uses the provided field or
the `value` field as the value of the returned rdata."""

    @resource_record_constructor
    def simple_resource_record_constructor(resource):
        """Build a simple rdata string from a dictionary containing its specification.

The expected field may be provided to this method's constructor, or its value may be
set in a field name `value`.
"""
        rdata = resource.get(field) or resource.get('value')
        if not rdata:
            raise KeyError(field)
        return rdata
    return simple_resource_record_constructor

@resource_record_constructor
def construct_NS_rdata(resource):
    """Build an NS rdata string from a dictionary containing its specification.

nsdname is the only value considered. If it is omitted, an appropritae value
will be created using the name field an additional nshost field. The computed
value will be `{nshost}.ns.{name}`.
"""
    return resource.get('nsdname',
                        '{nshost}.ns.{name}'.format(
                            nshost=resource['nshost'],
                            name=resource['name']
                        ))

@resource_record_constructor
def construct_SOA_rdata(resource):
    """Build an SOA rdata string from a dictionary containing its specification.

Fields are described in section 3.3.13 of https://www.ietf.org/rfc/rfc1035.txt

If mname or rname are omitted, appropriate values for them will be created
using the name field and an additional nshost field for mname. Those computed
values will be `{nshost}.ns.{name}` and `hostmaster.{name}` for mname and
rname respectfully.
"""
    return '{mname} {rname} {serial} {refresh} {retry} {expire} {minimum}'.format(
         mname=resource.get('mname',
                            '{nshost}.ns.{name}'.format(
                                 nshost=resource['nshost'],
                                 name=resource['name']
                             )),
         rname=resource.get('rname',
                            'hostmaster.{name}'.format(name=resource['name'])),
         serial=resource['serial'],
         refresh=resource['refresh'],
         retry=resource['retry'],
         expire=resource['expire'],
         minimum=resource['minimum']
    )

resource_record_constructors = dict(
    A=simple_resource_record_constructor_constructor('address'),
    CNAME=simple_resource_record_constructor_constructor('cname'),
    TXT=simple_resource_record_constructor_constructor('txt-data'),
    PTR=simple_resource_record_constructor_constructor('ptrdname'),
    SOA=construct_SOA_rdata,
    NS=construct_NS_rdata
)

def dns_resource_record(resource):
     """Build A resource record string from a dictionary containing its specification"""
     constructor = resource_record_constructors[resource['type']]
     return constructor(resource)

class FilterModule(object):
    """Convert a dictionary describing a DNS record to its string representation"""
    def filters(self):
        return dict(dns_resource_record=dns_resource_record)
