from marshmallow.decorators import tag_processor

ASYNC_PRE_DUMP = 'async_pre_dump'
ASYNC_POST_DUMP = 'async_post_dump'
ASYNC_PRE_LOAD = 'async_pre_load'
ASYNC_POST_LOAD = 'async_post_load'
ASYNC_VALIDATES = 'async_validates'
ASYNC_VALIDATES_SCHEMA = 'async_validates_schema'


def async_validates(field_name):
    return tag_processor(ASYNC_VALIDATES, None, False, field_name=field_name)


def async_validates_schema(fn=None, pass_many=False, pass_original=False, skip_on_field_errors=False):
    return tag_processor(ASYNC_VALIDATES_SCHEMA, fn, pass_many, pass_original=pass_original,
                         skip_on_field_errors=skip_on_field_errors)


def async_pre_dump(fn=None, pass_many=False):
    return tag_processor(ASYNC_PRE_DUMP, fn, pass_many)


def async_post_dump(fn=None, pass_many=False, pass_original=False):
    return tag_processor(ASYNC_POST_DUMP, fn, pass_many, pass_original=pass_original)


def async_pre_load(fn=None, pass_many=False):
    return tag_processor(ASYNC_PRE_LOAD, fn, pass_many)


def async_post_load(fn=None, pass_many=False, pass_original=False):
    return tag_processor(ASYNC_POST_LOAD, fn, pass_many, pass_original=pass_original)
