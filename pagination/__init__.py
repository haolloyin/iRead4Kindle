def paginate(request):
    page = int(request.REQUEST.get('page', '1'))
    return {"page": page}
