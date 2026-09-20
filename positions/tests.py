from django.test import RequestFactory, SimpleTestCase

from positions.views import index


class PositionsIndexTests(SimpleTestCase):

    def test_placeholder_renders_without_loading_positions(self):
        response = index(RequestFactory().get('/positions/'))

        self.assertContains(response, '<h1>Positions</h1>', html=True)
        self.assertContains(response, 'not yet available')
        self.assertContains(response, 'href="/bios/"')
        self.assertContains(response, 'href="/teams/"')
