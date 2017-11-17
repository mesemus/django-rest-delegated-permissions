# noinspection PyPackageRequirements
import re

import pytest
from django.db.models import Count, OuterRef, Exists, ExpressionWrapper, Value, BooleanField

from .app.models import Container, ItemA


@pytest.mark.django_db(transaction=True)
class TestExistsQuery:
    # region Tests

    def test_forward_foreign_key(self):
        inner_query = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query.filter(pk=OuterRef('parent')))) \
            .filter(__ex=True)
        assert str(outer_query.query), """
            SELECT "app_itema"."id", "app_itema"."name", "app_itema"."parent_id", 
                  EXISTS(
                      SELECT U0."id", U0."name", U0."item_c_id", True AS "__ex" FROM "app_container" U0 
                      WHERE (U0."id" IN (1, 2, 3, 4, 5) AND U0."id" = ("app_itema"."parent_id"))) AS "__ex" 
            FROM "app_itema" 
            WHERE EXISTS(
                      SELECT U0."id", U0."name", U0."item_c_id", True AS "__ex" FROM "app_container" U0 
                      WHERE (U0."id" IN (1, 2, 3, 4, 5) AND U0."id" = ("app_itema"."parent_id"))
                  ) = True        
        """.strip()

    @pytest.mark.xfail(reason="""
            Currently OuterRef fails silently on union, 
            just marking that fact to be notified when this is fixed in django
            """, strict=True)
    def test_outer_ref_on_union(self):
        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query1.union(inner_query2).filter(pk=OuterRef('parent')))) \
            .filter(__ex=True)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))

    @pytest.mark.xfail(reason="""
            Currently OuterRef fails silently on union, 
            just marking that fact to be notified when this is fixed in django
            """, strict=True)
    def test_outer_ref_on_union_parts(self):

        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query1.union(inner_query2))) \
            .filter(__ex=True)

        print(outer_query.query)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))

    def test_outer_ref_on_join_parts(self):

        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query1 | inner_query2)) \
            .filter(__ex=True)

        print(outer_query.query)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))

    def test_outer_ref_on_join(self):

        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))

        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))

        outer_query = ItemA.objects.annotate(__ex=Exists((inner_query1 | inner_query2).filter(pk=OuterRef('parent')))) \
            .filter(__ex=True)

        print(outer_query.query)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))

    @pytest.mark.xfail(reason="""
            Currently OuterRef fails silently on intersection, 
            just marking that fact to be notified when this is fixed in django
            """, strict=True)
    def test_outer_ref_on_intersection(self):
        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField()))
        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query1.intersection(inner_query2).filter(pk=OuterRef('parent')))) \
            .filter(__ex=True)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))

    @pytest.mark.xfail(reason="""
            Currently OuterRef fails silently on intersection, 
            just marking that fact to be notified when this is fixed in django
            """, strict=True)
    def test_outer_ref_on_intersection_parts(self):

        inner_query1 = Container.objects.filter(id__in=(1, 2, 3, 4, 5)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        inner_query2 = Container.objects.filter(id__in=(6,)) \
            .annotate(__ex=ExpressionWrapper(Value(True), output_field=BooleanField())) \
            .filter(pk=OuterRef('parent'))

        outer_query = ItemA.objects.annotate(__ex=Exists(inner_query1.intersection(inner_query2))) \
            .filter(__ex=True)

        print(outer_query.query)

        assert re.search(r'.*."id" = (.*."parent_id")', str(outer_query.query))


