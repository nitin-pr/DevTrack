import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from issues.models import CriticalIssue, Issue, LowPriorityIssue, Reporter
from issues.pagination import paginate
from issues.storage import (
    next_id,
    read_issues,
    read_reporters,
    write_issues,
    write_reporters,
)


def _parse_body(request):
    return json.loads(request.body.decode('utf-8') or '{}')


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def reporters_view(request):
    if request.method == 'POST':
        return create_reporter(request)
    return get_reporters(request)


def create_reporter(request):
    try:
        data = _parse_body(request)
        reporter = Reporter(
            id=data.get('id') or next_id(read_reporters()),
            name=data['name'],
            email=data['email'],
            team=data['team'],
        )
        reporter.validate()
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'error': f'Missing or invalid field: {e}'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    reporters = read_reporters()
    reporters.append(reporter.to_dict())
    write_reporters(reporters)
    return JsonResponse(reporter.to_dict(), status=201)


def get_reporters(request):
    reporters = read_reporters()

    reporter_id = request.GET.get('id')
    if reporter_id is not None:
        for reporter in reporters:
            if reporter['id'] == int(reporter_id):
                return JsonResponse(reporter, status=200)
        return JsonResponse({'error': 'Reporter not found'}, status=404)

    return JsonResponse(paginate(reporters, request), status=200)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def issues_view(request):
    if request.method == 'POST':
        return create_issue(request)
    return get_issues(request)


def create_issue(request):
    try:
        data = _parse_body(request)
        kwargs = dict(
            id=data.get('id') or next_id(read_issues()),
            title=data['title'],
            description=data['description'],
            status=data['status'],
            priority=data['priority'],
            reporter_id=data['reporter_id'],
        )
        if kwargs['priority'] == 'critical':
            issue = CriticalIssue(**kwargs)
        elif kwargs['priority'] == 'low':
            issue = LowPriorityIssue(**kwargs)
        else:
            issue = Issue(**kwargs)
        issue.validate()
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'error': f'Missing or invalid field: {e}'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    issues = read_issues()
    issues.append(issue.to_dict())
    write_issues(issues)

    response_data = issue.to_dict()
    response_data['message'] = issue.describe()
    return JsonResponse(response_data, status=201)


def get_issues(request):
    issues = read_issues()

    issue_id = request.GET.get('id')
    if issue_id is not None:
        for issue in issues:
            if issue['id'] == int(issue_id):
                return JsonResponse(issue, status=200)
        return JsonResponse({'error': 'Issue not found'}, status=404)

    status = request.GET.get('status')
    if status is not None:
        issues = [issue for issue in issues if issue['status'] == status]

    return JsonResponse(paginate(issues, request), status=200)
