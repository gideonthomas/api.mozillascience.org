import django_filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

from scienceapi.projects.models import Project, Category
from scienceapi.projects.serializers import (
    ProjectSerializer,
    CategorySerializer,
    ProjectUserSerializer,
    ProjectEventSerializer,
    ProjectExpandAllSerializer,
    ProjectWithGithubSerializer,
)


class ProjectSearchFilter(filters.SearchFilter):
    """
    We use a custom search filter to search based on a query
    like so - `?search=my_search_term`
    """
    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        return params.split(',')


class ProjectCustomFilter(filters.FilterSet):
    """
    We add custom filtering to allow you to filter by:
        * Category - pass the `?categories=` query parameter
        * Tag - pass the `?tags=` query parameter
    Both accept only one filter value i.e. one tag and/or one
    category.
    """
    tags = django_filters.CharFilter(
        name='tags__name',
        lookup_expr='iexact',
    )
    categories = django_filters.CharFilter(
        name='categories__name',
        lookup_expr='iexact',
    )

    class Meta:
        model = Project
        fields = ['tags', 'categories']


class ProjectsListView(ListAPIView):
    """
    A view that permits a GET to allow listing all the projects
    in the database

    **Route** - `/projects`

    **Query Parameters** -

    - `?search=` - Allows search terms
    - `?sort=` - Allows sorting of projects.
        - date_created - `?sort=date_created`
        - date_updated - `?sort=date_updated`

        *To sort in descending order, prepend the field with a '-', for e.g.
        `?sort=-date_updated`*

    - `?tags=` - Allows filtering projects by a specific tag
    - `?categories=` - Allows filtering projects by a specific category
    """
    queryset = Project.objects.public()
    serializer_class = ProjectSerializer
    pagination_class = PageNumberPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        ProjectSearchFilter,
        filters.OrderingFilter,
    )
    filter_class = ProjectCustomFilter
    ordering_fields = (
        'date_created',
        'date_updated',
    )
    search_fields = (
        'name',
        '=institution',
        'description',
        'short_description',
        '=license',
        '=tags__name',
        '=categories__name',
    )


class ProjectView(RetrieveAPIView):
    """
    A view that permits a GET to allow listing of a single project by providing
    its `id` as a parameter

    **Route** - `/projects/:id`

    **Query Parameters** -

    - `?expand=` -
    Forces the response to include basic
    information about a relation instead of just
    hyperlinking the relation associated
    with this project.

           Currently supported values are `?expand=users`,
           `?expand=events` and `?expand=users,events`

    """
    queryset = Project.objects.public()
    pagination_class = None

    def get_serializer_class(self):
        expand = self.request.query_params.get('expand')
        if expand is not None:
            expand = expand.split(',')
            if 'users' in expand and 'events' not in expand:
                return ProjectUserSerializer
            elif 'events' in expand and 'users' not in expand:
                return ProjectEventSerializer
            elif 'events' in expand and 'users' in expand:
                return ProjectExpandAllSerializer
            else:
                return ProjectWithGithubSerializer
        else:
            return ProjectWithGithubSerializer


class CategoryListView(ListAPIView):
    """
    A view that permits a GET to allow listing of all categories
    in the database
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
