from django.test import TestCase
from django.urls import reverse

from .forms import UpdateTradesForm

class UpdateTradesTests(TestCase):
    def setUp(self):
        self.url = reverse('update')

    def test_empty_url(self):
        res = self.client.post(self.url, {})
        form = res.context.get('form')
        self.assertEquals(res.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_url(self):
        res = self.client.post(self.url, { 'trades_url': 'asdf' })
        self.assertContains(res, '<div class="invalid-feedback">Invalid r/hardwareswap monthly trades URL</div>')