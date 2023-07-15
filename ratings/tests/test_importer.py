from django.test import TestCase
from django.db import transaction
from ratings.management.importer import import_ratings
from ratings.models import WespaRating, NationalRating

class ImportRatingsTest(TestCase):

    def test_import_wespa_ratings(self):
        content = [
            "NICKstateNAME                   punejul.tou 20230707",
            "GASI MYS Ganesh Asirvatham     636 2290 20181209",
            "QPRO USA Quackle Program        21 2153 20110925"
        ]

        with transaction.atomic():
            import_ratings(content, wespa=True)

        # Check if the database was updated correctly
        wespa_ratings = WespaRating.objects.all()
        national_ratings = NationalRating.objects.all()
        
        self.assertEqual(0, national_ratings.count())
        self.assertEqual(2, wespa_ratings.count())
        self.eval_content(wespa_ratings)

    def test_import_national_ratings(self):
        content = [
            "NICKstateNAME                   punejul.tou 20230707",
            "GASI MYS Ganesh Asirvatham     636 2290 20181209",
            "QPRO USA Quackle Program        21 2153 20110925"
        ]

        with transaction.atomic():
            import_ratings(content, wespa=False)

        # Check if the database was updated correctly
        wespa_ratings = WespaRating.objects.all()
        national_ratings = NationalRating.objects.all()
        
        self.assertEqual(2, national_ratings.count())
        self.assertEqual(0, wespa_ratings.count())
        self.eval_content(national_ratings)

    def eval_content(self, rat):
        self.assertEqual(rat[0].name, "Ganesh Asirvatham")
        self.assertEqual(rat[0].country, "MYS")
        self.assertEqual(rat[0].games, 636)
        self.assertEqual(rat[0].rating, 2290)
        self.assertEqual(rat[0].last, "20181209")
        
        self.assertEqual(rat[1].name, "Quackle Program")
        self.assertEqual(rat[1].country, "USA")
        self.assertEqual(rat[1].games, 21)
        self.assertEqual(rat[1].rating, 2153)
        self.assertEqual(rat[1].last, "20110925")

        