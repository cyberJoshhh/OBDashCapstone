STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'OBDash/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 