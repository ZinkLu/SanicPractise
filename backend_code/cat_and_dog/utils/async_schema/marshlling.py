# -*- coding: utf-8 -*-

from marshmallow import ValidationError, missing
from marshmallow.marshalling import Unmarshaller as _Unmarshaller, SCHEMA, FIELD, Marshaller as _Marshaller
from six import text_type


class Unmarshaller(_Unmarshaller):
    async def async_call_and_store(self, getter_func, data, field_name, field_obj, index=None):
        """
        take the fields validator and run it.
        """
        try:
            value = await getter_func(data)
        except ValidationError as err:  # Store validation errors
            self.error_kwargs.update(err.kwargs)
            self.error_fields.append(field_obj)
            self.error_field_names.append(field_name)
            errors = self.get_errors(index=index)
            # Warning: Mutation!
            if isinstance(err.messages, dict):
                errors[field_name] = err.messages
            elif isinstance(errors.get(field_name), dict):
                errors[field_name].setdefault(FIELD, []).extend(err.messages)
            else:
                errors.setdefault(field_name, []).extend(err.messages)
            # When a Nested field fails validation, the marshalled data is stored
            # on the ValidationError's data attribute
            value = err.data or missing
        return value

    async def async_run_validator(self, validator_func, output,
                                  original_data, fields_dict, index=None,
                                  many=False, pass_original=False):
        """
        take the schema validator and run it.
        """
        try:
            if pass_original:  # Pass original, raw data (before unmarshalling)
                res = await validator_func(output, original_data)
            else:
                res = await validator_func(output)
            if res is False:
                raise ValidationError(self.default_schema_validation_error)
        except ValidationError as err:
            errors = self.get_errors(index=index)
            self.error_kwargs.update(err.kwargs)
            # Store or reraise errors
            if err.field_names:
                field_names = err.field_names
                field_objs = [fields_dict[each] if each in fields_dict else None
                              for each in field_names]
            else:
                field_names = [SCHEMA]
                field_objs = []
            self.error_field_names = field_names
            self.error_fields = field_objs
            for field_name in field_names:
                if isinstance(err.messages, (list, tuple)):
                    # self.errors[field_name] may be a dict if schemas are nested
                    if isinstance(errors.get(field_name), dict):
                        errors[field_name].setdefault(
                            SCHEMA, []
                        ).extend(err.messages)
                    else:
                        errors.setdefault(field_name, []).extend(err.messages)
                elif isinstance(err.messages, dict):
                    errors.setdefault(field_name, []).append(err.messages)
                else:
                    errors.setdefault(field_name, []).append(text_type(err))


class Marshaller(_Marshaller):
    pass
