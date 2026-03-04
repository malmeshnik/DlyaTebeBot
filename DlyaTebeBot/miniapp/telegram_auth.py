from init_data_py import InitData


def check_telegram_auth(init_data: str, bot_token: str):
    try:
        init_data_obj = InitData.parse(init_data)

        if init_data_obj.validate(bot_token):
            return init_data_obj.to_dict()

        return None

    except Exception as e:
        print("Telegram auth error:", e)
        return None