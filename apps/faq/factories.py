import factory

import faq.models

__all__ = (
    'CategoryFactory',
    'QuestionFactory',
    'AnswerFactory',
)


class CategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'category-{}'.format(n))

    class Meta:
        model = faq.models.Category


class QuestionFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'title-{}'.format(n))
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = faq.models.Question


class AnswerFactory(factory.DjangoModelFactory):
    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = faq.models.Answer
