import factory
from factory.fuzzy import FuzzyText

import blog.models
import users.factories


class CategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'category-{}'.format(n))

    class Meta:
        model = blog.models.Category


class ArticleFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'blog text title-{}'.format(n))
    description = factory.Sequence(lambda n: 'blog text description-{}'.format(n))

    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = blog.models.Article


class CommentFactory(factory.DjangoModelFactory):
    description = FuzzyText(length=200)

    user = factory.SubFactory(users.factories.UserFactory)
    article = factory.SubFactory(ArticleFactory)

    class Meta:
        model = blog.models.Comment


class VoteFactory(factory.DjangoModelFactory):
    vote = blog.models.Vote.LIKE

    user = factory.SubFactory(users.factories.UserFactory)
    comment = factory.SubFactory(CommentFactory)
