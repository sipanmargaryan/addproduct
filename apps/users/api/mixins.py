from rest_framework.response import Response

import core.utils


class SaveSerializerMixin(metaclass=core.utils.RequiredAttrMeta):
    status_code = 200
    raise_exception = True
    save = True
    _required_attributes = ['serializer_class']

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=self.raise_exception)
        response = serializer.validated_data
        if self.save:
            response = serializer.save()

        return Response(response, status=self.status_code)


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()
