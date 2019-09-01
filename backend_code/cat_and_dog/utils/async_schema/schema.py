import functools
from collections import Mapping

from marshmallow import Schema as _Schema, UnmarshalResult, ValidationError, missing, utils, MarshalResult

from cat_and_dog.utils.async_schema.marshlling import Unmarshaller, Marshaller
from cat_and_dog.utils.async_schema.process import (ASYNC_PRE_DUMP,
                                                    ASYNC_POST_DUMP,
                                                    ASYNC_PRE_LOAD,
                                                    ASYNC_POST_LOAD,
                                                    ASYNC_VALIDATES,
                                                    ASYNC_VALIDATES_SCHEMA)


class Schema(_Schema):
    """
    ASYNC SCHEMA

    use::
        foo = await schema.async_load(data)
        bar = await schema.async_dump(instance)

    `async_load`, `async_dump` won't call original `load` and `dump`
    """

    async def _async_invoke_field_validators(self, unmarshal, data, many):
        """
        run field validators
        the validators:
            `validate`           original fields validator(NOT CALLED)
            `async_validate`     async fields validator(not used yet)

        .. seealso::
            :ref: `async_call_and_store`
        """
        # should call original fields validators first??
        # self._invoke_field_validators(unmarshal, data, many)

        for attr_name in self.__processors__[(ASYNC_VALIDATES, False)]:
            validator = getattr(self, attr_name)
            validator_kwargs = validator.__marshmallow_kwargs__[(ASYNC_VALIDATES, False)]
            field_name = validator_kwargs['field_name']

            try:
                field_obj = self.fields[field_name]
            except KeyError:
                if field_name in self.declared_fields:
                    continue
                raise ValueError('"{0}" field does not exist.'.format(field_name))

            if many:
                for idx, item in enumerate(data):
                    try:
                        value = item[field_obj.attribute or field_name]
                    except KeyError:
                        pass
                    else:
                        validated_value = await unmarshal.async_call_and_store(
                            getter_func=validator,
                            data=value,
                            field_name=field_obj.load_from or field_name,
                            field_obj=field_obj,
                            index=(idx if self.opts.index_errors else None)
                        )
                        if validated_value is missing:
                            data[idx].pop(field_name, None)
            else:
                try:
                    value = data[field_obj.attribute or field_name]
                except KeyError:
                    pass
                else:
                    validated_value = await unmarshal.async_call_and_store(
                        getter_func=validator,
                        data=value,
                        field_name=field_obj.load_from or field_name,
                        field_obj=field_obj
                    )
                    if validated_value is missing:
                        data.pop(field_name, None)

    async def _async_invoke_validators(self, unmarshal, pass_many, data, original_data, many, field_errors=False):
        """
        run schema validators
        the validators:
            `schema_validate`           original schema validator(NOT CALLED)
            `async_schema_validate`     async schema validator(used in foreign key check)

        .. seealso::
            :ref: `async_run_validator`
        """
        # should call the original schema_validator?
        # errors = self._invoke_validators(unmarshal, pass_many, data, original_data, many, field_errors)
        errors = dict()
        for attr_name in self.__processors__[(ASYNC_VALIDATES_SCHEMA, pass_many)]:
            validator = getattr(self, attr_name)
            validator_kwargs = validator.__marshmallow_kwargs__[(ASYNC_VALIDATES_SCHEMA, pass_many)]
            pass_original = validator_kwargs.get('pass_original', False)

            skip_on_field_errors = validator_kwargs['skip_on_field_errors']
            if skip_on_field_errors and field_errors:
                continue

            if pass_many:
                validator = functools.partial(validator, many=many)
            if many and not pass_many:
                for idx, item in enumerate(data):
                    try:
                        await unmarshal.async_run_validator(validator,
                                                            item, original_data, self.fields, many=many,
                                                            index=idx, pass_original=pass_original)
                    except ValidationError as err:
                        errors.update(err.messages)
            else:
                try:
                    await unmarshal.async_run_validator(validator,
                                                        data, original_data, self.fields, many=many,
                                                        pass_original=pass_original)
                except ValidationError as err:
                    errors.update(err.messages)
        if errors:
            raise ValidationError(errors)
        return None

    async def _async_invoke_load_processors(self, tag_name, data, many, original_data=None):
        """wrapper fo `_async_invoke_processors`

        .. seealso::
            :ref:   _async_invoke_processors
        """
        # This has to invert the order of the dump processors, so run the pass_many
        # processors first.
        data = await self._async_invoke_processors(tag_name, pass_many=True,
                                                   data=data, many=many, original_data=original_data)
        data = await self._async_invoke_processors(tag_name, pass_many=False,
                                                   data=data, many=many, original_data=original_data)
        return data

    async def _async_invoke_processors(self, tag_name, pass_many, data, many, original_data=None):
        """make processors async
        the processors:
            `async_pre_load`, `async_post_load`
            `async_pre_dump`, `async_post_dump` (to do)
        """
        for attr_name in self.__processors__[(tag_name, pass_many)]:
            # This will be a bound method.
            processor = getattr(self, attr_name)

            processor_kwargs = processor.__marshmallow_kwargs__[(tag_name, pass_many)]
            pass_original = processor_kwargs.get('pass_original', False)

            if pass_many:
                if pass_original:
                    data = utils.if_none(await processor(data, many, original_data), data)
                else:
                    data = utils.if_none(await processor(data, many), data)
            elif many:
                if pass_original:
                    data = [utils.if_none(await processor(item, original_data), item)
                            for item in data]
                else:
                    data = [utils.if_none(await processor(item), item) for item in data]
            else:
                if pass_original:
                    data = utils.if_none(await processor(data, original_data), data)
                else:
                    data = utils.if_none(await processor(data), data)
        return data

    async def _async_do_load(self, data, many=None, partial=None, postprocess=True):
        """load the data"
            1./ validate the data by `async_validate`, `async_validate_schema`, `validate`, `validate_schema`
            2./ process the data by `async_pre_load`, `async_post_load`

        """
        unmarshal = Unmarshaller()
        errors = {}
        many = self.many if many is None else bool(many)
        if partial is None:
            partial = self.partial
        try:
            # 1. async_pre_load
            processed_data = await self._async_invoke_load_processors(
                ASYNC_PRE_LOAD,
                data,
                many,
                original_data=data)
        except ValidationError as err:
            errors = err.normalized_messages()
            result = None
        if not errors:
            try:
                result = unmarshal(
                    processed_data,
                    self.fields,
                    many=many,
                    partial=partial,
                    dict_class=self.dict_class,
                    index_errors=self.opts.index_errors,
                )
            except ValidationError as error:
                result = error.data
            await self._async_invoke_field_validators(unmarshal, data=result, many=many)
            errors = unmarshal.errors
            field_errors = bool(errors)
            # Run schema-level migration
            try:
                await self._async_invoke_validators(unmarshal, pass_many=True, data=result, original_data=data,
                                                    many=many, field_errors=field_errors)
            except ValidationError as err:
                errors.update(err.messages)
            try:
                await self._async_invoke_validators(unmarshal, pass_many=False, data=result, original_data=data,
                                                    many=many, field_errors=field_errors)
            except ValidationError as err:
                errors.update(err.messages)
        # Run post processors
        if not errors and postprocess:
            try:
                result = self._async_invoke_load_processors(
                    ASYNC_POST_LOAD,
                    result,
                    many,
                    original_data=data)
            except ValidationError as err:
                errors = err.normalized_messages()
        if errors:
            # TODO: Remove self.__error_handler__ in a later release
            # if self.__error_handler__ and callable(self.__error_handler__):
            #     self.__error_handler__(errors, data)
            exc = ValidationError(
                errors,
                field_names=unmarshal.error_field_names,
                fields=unmarshal.error_fields,
                data=data,
                **unmarshal.error_kwargs
            )
            self.handle_error(exc, data)
            if self.strict:
                raise exc

        return await result, errors

    async def async_load(self, data, many=None, partial=None):
        """the async_load function DO NOT handler the original
        processors function like `post_load` or `pre_load`.
        but it uses the original validators.
        """
        result, errors = await self._async_do_load(data, many, partial=partial, postprocess=True)
        return UnmarshalResult(data=result, errors=errors)

    async def _async_invoke_dump_processors(self, tag_name, data, many, original_data=None):
        data = await self._async_invoke_processors(tag_name, pass_many=False,
                                                   data=data, many=many, original_data=original_data)
        data = await self._async_invoke_processors(tag_name, pass_many=True,
                                                   data=data, many=many, original_data=original_data)
        return data

    async def async_dump(self, obj, many=None, update_fields=True, **kwargs):
        # Callable marshalling object
        marshal = Marshaller(prefix=self.prefix)
        errors = {}
        many = self.many if many is None else bool(many)
        if many and utils.is_iterable_but_not_string(obj):
            obj = list(obj)

        if self._has_processors:
            try:
                processed_obj = await self._async_invoke_dump_processors(
                    ASYNC_PRE_DUMP,
                    obj,
                    many,
                    original_data=obj)
            except ValidationError as error:
                errors = error.normalized_messages()
                result = None
        else:
            processed_obj = obj

        if not errors:
            if update_fields:
                obj_type = type(processed_obj)
                if obj_type not in self._types_seen:
                    self._update_fields(processed_obj, many=many)
                    if not isinstance(processed_obj, Mapping):
                        self._types_seen.add(obj_type)

            try:
                preresult = marshal(
                    processed_obj,
                    self.fields,
                    many=many,
                    # TODO: Remove self.__accessor__ in a later release
                    accessor=self.get_attribute or self.__accessor__,
                    dict_class=self.dict_class,
                    index_errors=self.opts.index_errors,
                    **kwargs
                )
            except ValidationError as error:
                errors = marshal.errors
                preresult = error.data

            result = self._postprocess(preresult, many, obj=obj)

        if not errors and self._has_processors:
            try:
                result = await self._async_invoke_dump_processors(
                    ASYNC_POST_DUMP,
                    result,
                    many,
                    original_data=obj)
            except ValidationError as error:
                errors = error.normalized_messages()
        if errors:
            # TODO: Remove self.__error_handler__ in a later release
            if self.__error_handler__ and callable(self.__error_handler__):
                self.__error_handler__(errors, obj)
            exc = ValidationError(
                errors,
                field_names=marshal.error_field_names,
                fields=marshal.error_fields,
                data=obj,
                **marshal.error_kwargs
            )
            self.handle_error(exc, obj)
            if self.strict:
                raise exc

        return MarshalResult(result, errors)
