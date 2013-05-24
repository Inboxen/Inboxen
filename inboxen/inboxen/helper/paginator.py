from django.core.paginator import InvalidPage

def look_back(paginator, limit=None):
    try:
        previous = paginator.previous_page_number()
    except InvalidPage:
        return []

    previous = [
        {
            "page":previous,
            "active":False,
        }
    ]

    if limit == 1:
        return previous
    
    return look_back(
        paginator.paginator.page(previous[0]["page"]), 
        limit-1,
    ) + previous

def look_forward(paginator, limit=None):
    try:
        n = paginator.next_page_number()
    except InvalidPage:
        return []

    n = [
            {
                "page":n,
                "active":False,
            }
    ]

    if limit == 1:
        return n

    return n + look_forward(
        paginator.paginator.page(n[0]["page"]),
        limit-1,
    )

def page(paginator):
    pages = []

    if paginator.has_previous():
        pages += look_back(paginator, 2)
    
    pages += [
        {
            "page":paginator.number,
            "active":True,
        }
    ]

    if paginator.has_next():
        pages += look_forward(paginator, 2)



    return pages
