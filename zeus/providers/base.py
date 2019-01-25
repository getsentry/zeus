from jsonschema import Draft4Validator, validators


# XXX(dcramer): I'd prefer this copy the value and fill in defaults
# but I dont care enough to learn the inner workings of the jsonschema
# package
# https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})


DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)


class Provider(object):
    def get_config(self):
        return {
            # the type is inferred as object for the root level
            # 'type': 'object',
            "properties": {},
            "required": [],
        }

    def get_name(self, config):
        raise NotImplementedError

    def validate_config(self, data):
        schema = self.get_config()
        schema["type"] = "object"
        DefaultValidatingDraft4Validator(schema).validate(data)
