from backend_main.settings import APP_MODE, TESTING_DB_ACCESS_SECRET_HEADER, TESTING_DB_ACCESS_SECRET


def validate_db_access_secret(request):
    db_access_secret = request.headers.get(TESTING_DB_ACCESS_SECRET_HEADER, None)
    if APP_MODE != "TESTING":
        return {
            'success': False,
            'error': {
                'code': "not_in_the_mood_for_this",
            },
        }
    
    if db_access_secret is None:
        return {
            'success': False,
            'error': {
                'code': "no_db_access_secret_header_provided",
            },
        }
    
    if db_access_secret != TESTING_DB_ACCESS_SECRET:
        return {
            'success': False,
            'error': {
                'code': "invalid_db_access_secret",
            },
        }
    
    return {
        'success': True,
    }
    