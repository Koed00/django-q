import subprocess


def generate_mo_files():
    subprocess.run(["django-admin", "compilemessages"])


if __name__ == "__main__":
    generate_mo_files()
