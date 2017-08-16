def replace_field(value, shared_fields, field):
    return dict([(key, shared_fields[key]) for key in shared_fields if key != field] + [(field, value)])

def merge(override, original):
    return dict([(key, original[key]) for key in original if key not in override], **override)


class FilterModule(object):
    def filters(self):
        return dict(merge=merge,
                    replace_field=replace_field)
