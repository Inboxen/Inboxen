from wagtail.wagtailcore import hooks


@hooks.register('before_serve_page')
def set_page_on_request(page, request, serve_args, serve_kwargs):
    request.page = page
