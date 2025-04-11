from django.db import models

class Annotation(models.Model):
    group_id = models.IntegerField()
    pdf_url = models.TextField()
    data = models.JSONField()

    def __str__(self):
        return f"Annotations for Group {self.group_id} - {self.pdf_url}"

