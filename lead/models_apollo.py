from django.db import models

class ApolloPagination(models.Model):
    person_titles = models.JSONField(default=list, null=True, blank=True)
    person_locations = models.JSONField(default=list, null=True, blank=True)
    organization_num_employees_ranges = models.JSONField(default=list, null=True, blank=True)
    organization_industries = models.JSONField(default=list, null=True, blank=True)
    page = models.IntegerField()
    per_page = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'apollo_pagination_history'
        ordering = ['-created_on']
        verbose_name = "Apollo Pagination History"