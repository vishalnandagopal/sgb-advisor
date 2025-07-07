from dotenv import load_dotenv

# Need to load dotenv before importing/running any file, since they use API keys from env modules
load_dotenv(".env")


def main() -> None:
    "Entry fuction for the script"
    from src.sgb_advisor import runner as runner

    runner()


if __name__ == "__main__":
    main()
