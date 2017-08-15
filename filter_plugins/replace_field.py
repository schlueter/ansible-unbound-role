def replace_field(value, shared_fields, field):
    return dict([(key, shared_fields[key]) for key in shared_fields if key != field] + [(field, value)])

class FilterModule(object):
    ''' A filter to apply default permissions to a list of vhosts '''
    def filters(self):
        return dict(replace_field=replace_field)
