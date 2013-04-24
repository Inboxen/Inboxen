def error_out(request=None, template="error.html", page="Error", message="There has been a server error"):
    """ Produces an error response """

    context = {
        "page":page,
        "error":message,
    }

    return render(request, template, context)
