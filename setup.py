from pip._internal.cli.main import main


common_packages = [
    'aiofiles==23.2.1',
    'aiogram==3.6.0',
    'aiohttp==3.9.5',
    'aiosignal==1.3.1',
    'annotated-types==0.6.0',
    'attrs==23.2.0',
    'certifi==2024.2.2',
    'frozenlist==1.4.1',
    'idna==3.7',
    'magic-filter==1.0.12',
    'multidict==6.0.5',
    'pydantic==2.7.1',
    'pydantic_core==2.18.2',
    'typing_extensions==4.11.0',
    'yarl==1.9.4'

]


def install_packages(packages_list: list[str]):
    for pkg in packages_list:
        main(["install", "-U", pkg])


if __name__ == '__main__':
    install_packages(common_packages)
