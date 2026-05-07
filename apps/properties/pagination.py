from rest_framework.pagination import PageNumberPagination 

class HomeMatchPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_query_param = "page_size"
