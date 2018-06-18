import json
from game.models import Property


def condition_text_checker(condition_text, session_character):
    condition_dict = json.loads(condition_text)
    for condition in condition_dict:
        property_pk, condition_type, condition_value = condition
        try:
            property = Property.objects.get(pk=property_pk)
            session_value = property.get_session_value(session_character)
        except Property.DoesNotExist:
            return False

        if condition_type == "==":
            if session_value == condition_value:
                continue
            else:
                return False
        elif condition_type == ">=":
            if session_value >= condition_value:
                continue
            else:
                return False
        elif condition_type == ">":
            if session_value > condition_value:
                continue
            else:
                return False
        elif condition_type == "<=":
            if session_value <= condition_value:
                continue
            else:
                return False
        elif condition_type == "<":
            if session_value < condition_value:
                continue
            else:
                return False
        elif condition_type == "!=":
            if session_value != condition_value:
                continue
            else:
                return False

    return True