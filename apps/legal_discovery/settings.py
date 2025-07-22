from .models import UserSetting
from .database import db

def get_user_settings(user_id=1):
    """
    Retrieves user settings from the database.
    For now, we'll use a default user_id of 1.
    """
    return UserSetting.query.filter_by(user_id=user_id).first()

def save_user_settings(data, user_id=1):
    """
    Saves user settings to the database.
    """
    settings = get_user_settings(user_id)
    if not settings:
        settings = UserSetting(user_id=user_id)

    settings.courtlistener_api_key = data.get('courtlistener_api_key')
    settings.gemini_api_key = data.get('gemini_api_key')
    settings.california_codes_url = data.get('california_codes_url')

    db.session.add(settings)
    db.session.commit()
    return settings
