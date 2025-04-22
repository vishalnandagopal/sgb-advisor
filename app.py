from dotenv import load_dotenv

# Need to load dotenv before importing/running any file, since they use API keys from env modules
load_dotenv(".env")


def main():
    "Entry fuction for the script"
    from src.sgb_advisor import get_sgbs, notify

    sgbs = get_sgbs()
    notify(sgbs)


if __name__ == "__main__":
    main()
