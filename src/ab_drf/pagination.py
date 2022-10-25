"""
Pagination
==========
"""

from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 9

    def get_page_links(self):
        page_links = self.get_html_context()["page_links"]
        return [
            {"number": pl.number, "url": pl.url, "is_active": pl.is_active}
            for pl in page_links
        ]

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                # "has_next": self.page.has_next(),
                # "has_previous": self.page.has_previous(),
                # "has_other_pages": self.page.has_other_pages(),
                # "next_page_number": self.page.next_page_number(),
                # "previous_page_number": self.page.previous_page_number(),
                "current_page": self.page.number,
                "num_pages": self.page.paginator.num_pages,
                # "page_range": [p for p in self.page.paginator.page_range],
                "page_links": self.get_page_links(),
                "start_index": self.page.start_index(),
                "end_index": self.page.end_index(),
                "count": self.page.paginator.count,
                "results": data,
            }
        )
