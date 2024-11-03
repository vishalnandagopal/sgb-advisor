from dotenv import load_dotenv

# Need to load dotenv before running any file, since they use API keys from env modules
load_dotenv(".env")


def run():
    from src.sgb_advisor import get_sgbs, notify

    notify(get_sgbs())


run()
