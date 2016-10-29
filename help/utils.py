def app_reverse(page, site, viewname, args=None, kwargs=None):
    """Reverse a URL for an app that is behind an AppPage"""
    relative_url = page.reverse(viewname, args=args, kwargs=kwargs)
    page_url = page.relative_url(site)
    page_url = page_url.rstrip("/")

    return page_url + relative_url
