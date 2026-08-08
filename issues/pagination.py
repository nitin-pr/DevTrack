DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def paginate(records, request):
    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.GET.get('page_size', DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        page_size = DEFAULT_PAGE_SIZE

    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

    count = len(records)
    total_pages = max((count + page_size - 1) // page_size, 1)
    page = min(page, total_pages)

    start = (page - 1) * page_size
    end = start + page_size

    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'results': records[start:end],
    }
