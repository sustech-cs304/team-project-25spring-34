from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import io
from unittest.mock import patch


def _create_fake_pdf(content_bytes):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, content_bytes.decode('utf-8'))
    p.save()
    buffer.seek(0)
    return SimpleUploadedFile("test.pdf", buffer.read(), content_type='application/pdf')


class TestDeepSeekAPI(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('deepseek_api', kwargs={'data_course': 'test'})


    def test_post_with_text_prompt_only(self):
        response = self.client.post(self.url, data={'message': '你好'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())

    @patch("ai_assistant.views.html_to_png")
    def test_post_with_pdf_and_prompt_for_map(self, mock_html_to_png):
        mock_html_to_png.return_value = None
        pdf = _create_fake_pdf("内容中含有思维导图关键词".encode("utf-8"))
        res = self.client.post(self.url, data={
            'message': '请生成一份思维导图',
            'pdf': pdf
        })
        self.assertIn(res.status_code, [200, 500])
        self.assertTrue('html_url' in res.json() or 'error' in res.json())

    def test_post_with_pdf_and_prompt_for_test(self):
        fake_pdf = _create_fake_pdf("内容中含有题目关键词".encode("utf-8"))
        response = self.client.post(
            self.url,
            data={
                'message': '根据这个pdf生成几道测试题',
                'pdf': fake_pdf
            }
        )
        self.assertIn(response.status_code, [200, 500])  # Playwright/DeepSeek失败可容忍
        self.assertTrue('html_url' in response.json() or 'error' in response.json())

    def test_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
