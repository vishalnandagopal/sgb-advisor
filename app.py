from dotenv import load_dotenv

load_dotenv(".env")
# Need to load dotenv before running any file, since they use API keys from env modules


def run():
    from src.sgb_advisor import get_sgbs, notify

    notify(get_sgbs())


run()
